"""
IntelliWealth – Risk Intelligence Engine
Core analytics engine for portfolio risk assessment.

Risk Logic:
  - equity > 80%  → risk = HIGH
  - gold diversification → reduces risk
  - Calculates: concentration, sector exposure, diversification score, volatility, risk level
"""

import logging
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.market_data import MarketData
from app.models.risk_metrics import RiskMetrics
from app.redis_client import CacheService
from app.schemas.risk_metrics import ConcentrationBreakdown, RiskAssessmentResponse

logger = logging.getLogger("intelliwealth.risk")
settings = get_settings()

# ---- Asset Type → Sector Mapping ----
ASSET_TYPE_SECTOR_MAP: Dict[str, str] = {
    "stocks": "Equity",
    "mutual_funds": "Equity",
    "bonds": "Fixed Income",
    "gold": "Commodities",
    "crypto": "Digital Assets",
    "cash": "Cash & Equivalents",
}

# ---- Base Volatility Weights (annualized estimates) ----
ASSET_VOLATILITY_MAP: Dict[str, float] = {
    "stocks": 18.0,
    "mutual_funds": 14.0,
    "bonds": 5.0,
    "gold": 12.0,
    "crypto": 55.0,
    "cash": 0.5,
}


class RiskEngine:
    """
    Computes portfolio risk intelligence including:
    - Portfolio concentration score
    - Sector exposure mapping
    - Diversification score (0–100)
    - Weighted volatility
    - Risk level classification (LOW / MODERATE / HIGH / CRITICAL)
    """

    def __init__(self) -> None:
        self._cache = CacheService()

    def assess_portfolio_risk(
        self,
        db: Session,
        portfolio_id: UUID,
        assets: List[dict],
    ) -> RiskAssessmentResponse:
        """
        Run full risk assessment on a portfolio.

        Args:
            db: Database session
            portfolio_id: UUID of the portfolio
            assets: List of asset dicts with keys: asset_type, current_value

        Returns:
            RiskAssessmentResponse with complete risk intelligence.
        """
        # Check cache first
        cache_key = str(portfolio_id)
        cached = self._cache.get_risk(cache_key)
        if cached:
            cached["cached"] = True
            return RiskAssessmentResponse(**cached)

        logger.info("Computing risk assessment for portfolio %s", portfolio_id)

        if not assets:
            return self._empty_assessment(portfolio_id)

        total_value = sum(a.get("current_value", 0.0) for a in assets)
        if total_value <= 0:
            return self._empty_assessment(portfolio_id)

        # ---- Step 1: Allocation by asset type ----
        allocation = self._compute_allocation(assets, total_value)

        # ---- Step 2: Sector exposure ----
        sector_exposure = self._compute_sector_exposure(allocation)

        # ---- Step 3: Concentration score ----
        concentration = self._compute_concentration(allocation)

        # ---- Step 4: Diversification score ----
        diversification = self._compute_diversification(allocation)

        # ---- Step 5: Weighted volatility ----
        volatility = self._compute_volatility(allocation)

        # ---- Step 6: Risk score & level ----
        risk_score, risk_level = self._compute_risk_level(
            allocation, concentration, diversification, volatility
        )

        # ---- Step 7: Concentration breakdown ----
        breakdown = self._build_concentration_breakdown(allocation)

        # ---- Step 8: Recommendations ----
        recommendations = self._generate_recommendations(
            allocation, risk_level, concentration, diversification
        )

        # ---- Step 9: Persist to DB ----
        metrics = RiskMetrics(
            portfolio_id=portfolio_id,
            risk_score=round(risk_score, 2),
            risk_level=risk_level,
            concentration_score=round(concentration, 2),
            diversification_score=round(diversification, 2),
            volatility=round(volatility, 2),
            sector_exposure=sector_exposure,
            recommendations="; ".join(recommendations),
        )
        db.add(metrics)
        db.commit()
        db.refresh(metrics)

        result = RiskAssessmentResponse(
            portfolio_id=portfolio_id,
            risk_score=round(risk_score, 2),
            risk_level=risk_level,
            concentration_score=round(concentration, 2),
            diversification_score=round(diversification, 2),
            volatility=round(volatility, 2),
            sector_exposure=sector_exposure,
            concentration_breakdown=breakdown,
            recommendations=recommendations,
            computed_at=datetime.utcnow().isoformat(),
        )

        # Cache the result
        self._cache.set_risk(cache_key, result.model_dump())
        logger.info(
            "Risk assessment complete: portfolio=%s level=%s score=%.2f",
            portfolio_id, risk_level, risk_score,
        )

        return result

    # ================================================================
    # Computation Methods
    # ================================================================

    def _compute_allocation(
        self, assets: List[dict], total_value: float
    ) -> Dict[str, float]:
        """
        Build allocation map: asset_type → percentage of total value.
        """
        allocation: Dict[str, float] = {}
        for asset in assets:
            atype = asset.get("asset_type", "cash")
            value = asset.get("current_value", 0.0)
            pct = (value / total_value) * 100.0 if total_value > 0 else 0.0
            allocation[atype] = allocation.get(atype, 0.0) + pct
        return {k: round(v, 2) for k, v in allocation.items()}

    def _compute_sector_exposure(
        self, allocation: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Map asset type allocation to sector exposure percentages.
        """
        exposure: Dict[str, float] = {}
        for atype, pct in allocation.items():
            sector = ASSET_TYPE_SECTOR_MAP.get(atype, "Other")
            exposure[sector] = exposure.get(sector, 0.0) + pct
        return {k: round(v, 2) for k, v in exposure.items()}

    def _compute_concentration(self, allocation: Dict[str, float]) -> float:
        """
        Herfindahl-Hirschman Index (HHI) normalized to 0–100.
        Higher = more concentrated = higher risk.
        """
        if not allocation:
            return 0.0
        hhi = sum((pct / 100.0) ** 2 for pct in allocation.values())
        # Normalize: min HHI = 1/N, max HHI = 1.0
        n = len(allocation)
        if n <= 1:
            return 100.0
        min_hhi = 1.0 / n
        normalized = (hhi - min_hhi) / (1.0 - min_hhi) if (1.0 - min_hhi) > 0 else 0.0
        return round(normalized * 100.0, 2)

    def _compute_diversification(self, allocation: Dict[str, float]) -> float:
        """
        Diversification score (0–100). Higher = better diversified.
        Factors: number of asset types, evenness of distribution.
        """
        n = len(allocation)
        if n == 0:
            return 0.0

        # Type count score: capped at 6 types
        type_score = min(n / 6.0, 1.0) * 40.0

        # Distribution evenness (inverse of concentration)
        concentration = self._compute_concentration(allocation)
        evenness_score = (100.0 - concentration) * 0.4

        # Bonus for having gold (reduces risk per requirements)
        gold_bonus = 0.0
        gold_pct = allocation.get("gold", 0.0)
        if gold_pct >= 5.0:
            gold_bonus = min(gold_pct / 20.0, 1.0) * 20.0

        return round(min(type_score + evenness_score + gold_bonus, 100.0), 2)

    def _compute_volatility(self, allocation: Dict[str, float]) -> float:
        """
        Portfolio weighted volatility using base asset volatility estimates.
        """
        weighted_vol = 0.0
        for atype, pct in allocation.items():
            base_vol = ASSET_VOLATILITY_MAP.get(atype, 10.0)
            weighted_vol += (pct / 100.0) * base_vol
        return round(weighted_vol, 2)

    def _compute_risk_level(
        self,
        allocation: Dict[str, float],
        concentration: float,
        diversification: float,
        volatility: float,
    ) -> Tuple[float, str]:
        """
        Compute overall risk score (0–100) and classify risk level.

        Key rule: equity > 80% → risk = HIGH (per requirements).
        Gold diversification reduces risk (per requirements).
        """
        # Equity exposure (stocks + mutual_funds)
        equity_pct = allocation.get("stocks", 0.0) + allocation.get("mutual_funds", 0.0)

        # Base risk score: weighted combination
        score = 0.0
        score += concentration * 0.25  # 25% weight: concentration
        score += (100.0 - diversification) * 0.25  # 25% weight: lack of diversification
        score += min(volatility / 55.0, 1.0) * 100.0 * 0.30  # 30% weight: volatility (normalized to crypto max)
        score += min(equity_pct / 100.0, 1.0) * 100.0 * 0.20  # 20% weight: equity exposure

        # ---- Mandatory rule: equity > 80% → force HIGH ----
        if equity_pct > settings.RISK_HIGH_EQUITY_THRESHOLD:
            score = max(score, 70.0)  # Ensure at least HIGH threshold

        # ---- Gold reduction factor ----
        gold_pct = allocation.get("gold", 0.0)
        if gold_pct > 0:
            reduction = min(gold_pct / 100.0, 0.20) * settings.RISK_GOLD_REDUCTION_FACTOR * 100.0
            score = max(score - reduction, 0.0)

        score = min(round(score, 2), 100.0)

        # Classify
        if score >= 75.0:
            level = "CRITICAL"
        elif score >= 50.0:
            level = "HIGH"
        elif score >= 25.0:
            level = "MODERATE"
        else:
            level = "LOW"

        # Force HIGH if equity exceeds threshold (even after gold reduction)
        if equity_pct > settings.RISK_HIGH_EQUITY_THRESHOLD and level == "MODERATE":
            level = "HIGH"
            score = max(score, 50.0)

        return score, level

    def _build_concentration_breakdown(
        self, allocation: Dict[str, float]
    ) -> List[ConcentrationBreakdown]:
        """Build per-type concentration risk contribution."""
        breakdown = []
        for atype, pct in sorted(allocation.items(), key=lambda x: x[1], reverse=True):
            if pct >= 40.0:
                risk = "high"
            elif pct >= 20.0:
                risk = "moderate"
            else:
                risk = "low"
            breakdown.append(
                ConcentrationBreakdown(
                    asset_type=atype,
                    allocation_percent=pct,
                    risk_contribution=risk,
                )
            )
        return breakdown

    def _generate_recommendations(
        self,
        allocation: Dict[str, float],
        risk_level: str,
        concentration: float,
        diversification: float,
    ) -> List[str]:
        """Generate actionable risk recommendations."""
        recs: List[str] = []
        equity_pct = allocation.get("stocks", 0.0) + allocation.get("mutual_funds", 0.0)

        # Equity concentration warning
        if equity_pct > settings.RISK_HIGH_EQUITY_THRESHOLD:
            recs.append(
                f"CRITICAL: Equity allocation at {equity_pct:.1f}% exceeds the {settings.RISK_HIGH_EQUITY_THRESHOLD:.0f}% threshold. "
                f"Rebalance by shifting {equity_pct - 60:.0f}% into bonds, gold, or other asset classes."
            )

        # Gold recommendation
        gold_pct = allocation.get("gold", 0.0)
        if gold_pct < 5.0:
            recs.append(
                "Consider adding gold allocation (target: 5–15%). Gold acts as a hedge "
                "against inflation and reduces overall portfolio volatility."
            )

        # Diversification
        if diversification < 40.0:
            recs.append(
                f"Diversification score is low ({diversification:.0f}/100). "
                f"Add exposure to at least {settings.RISK_DIVERSIFICATION_MIN_TYPES} asset types for better risk management."
            )

        # Crypto exposure
        crypto_pct = allocation.get("crypto", 0.0)
        if crypto_pct > 20.0:
            recs.append(
                f"Crypto allocation at {crypto_pct:.1f}% introduces high volatility. "
                "Consider reducing to under 15% and reallocating to fixed income."
            )

        # Bond underweight
        bond_pct = allocation.get("bonds", 0.0)
        if bond_pct < 10.0 and risk_level in ("HIGH", "CRITICAL"):
            recs.append(
                "Bond allocation is below 10% in a high-risk portfolio. "
                "Increasing fixed income exposure would improve downside protection."
            )

        # Cash drag
        cash_pct = allocation.get("cash", 0.0)
        if cash_pct > 25.0:
            recs.append(
                f"Cash allocation at {cash_pct:.1f}% may create return drag. "
                "Consider deploying idle cash into diversified assets."
            )

        # Positive note if well-balanced
        if not recs:
            recs.append(
                "Portfolio is well-diversified with balanced allocation across asset classes. "
                "Continue monitoring sector exposure and rebalance quarterly."
            )

        return recs

    def _empty_assessment(self, portfolio_id: UUID) -> RiskAssessmentResponse:
        """Return a neutral assessment for empty portfolios."""
        return RiskAssessmentResponse(
            portfolio_id=portfolio_id,
            risk_score=0.0,
            risk_level="LOW",
            concentration_score=0.0,
            diversification_score=0.0,
            volatility=0.0,
            sector_exposure={},
            concentration_breakdown=[],
            recommendations=["Portfolio has no assets. Add investments to receive risk intelligence."],
            computed_at=datetime.utcnow().isoformat(),
        )

    # ================================================================
    # Historical Risk Query
    # ================================================================

    def get_risk_history(
        self, db: Session, portfolio_id: UUID, limit: int = 30
    ) -> List[dict]:
        """Retrieve historical risk assessments for a portfolio."""
        rows = (
            db.query(RiskMetrics)
            .filter(RiskMetrics.portfolio_id == portfolio_id)
            .order_by(RiskMetrics.computed_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": str(r.id),
                "risk_score": r.risk_score,
                "risk_level": r.risk_level,
                "diversification_score": r.diversification_score,
                "volatility": r.volatility,
                "computed_at": r.computed_at.isoformat(),
            }
            for r in rows
        ]
