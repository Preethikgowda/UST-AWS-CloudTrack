"""
IntelliWealth – Market Data Service
Business logic for asset pricing, trend analysis, and volatility computation.
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.market_data import MarketData
from app.models.sector_data import SectorData
from app.redis_client import CacheService
from app.schemas.market_data import (
    MarketAssetResponse,
    MarketAssetsListResponse,
    MarketTrendResponse,
    TrendPoint,
    VolatilityItem,
    VolatilityResponse,
)
from app.schemas.sector_data import SectorAnalysisResponse, SectorItem

logger = logging.getLogger("intelliwealth.market")


class MarketService:
    """Encapsulates all market data query and analytics logic."""

    def __init__(self) -> None:
        self._cache = CacheService()

    # ================================================================
    # GET /market/assets
    # ================================================================

    def get_assets(
        self,
        db: Session,
        asset_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> MarketAssetsListResponse:
        """
        Return latest market data for all tracked assets.
        Uses Redis cache with fallback to PostgreSQL.
        """
        cache_key = f"assets:{asset_type or 'all'}:{limit}:{offset}"
        cached = self._cache.get_analytics(cache_key)
        if cached:
            return MarketAssetsListResponse(**cached, cached=True)

        # Subquery: latest timestamp per asset
        latest_sq = (
            db.query(
                MarketData.asset_name,
                func.max(MarketData.timestamp).label("max_ts"),
            )
            .group_by(MarketData.asset_name)
            .subquery()
        )

        query = (
            db.query(MarketData)
            .join(
                latest_sq,
                (MarketData.asset_name == latest_sq.c.asset_name)
                & (MarketData.timestamp == latest_sq.c.max_ts),
            )
        )

        if asset_type:
            query = query.filter(MarketData.asset_type == asset_type)

        total = query.count()
        rows = query.order_by(MarketData.asset_name).offset(offset).limit(limit).all()

        assets = [MarketAssetResponse.model_validate(r) for r in rows]
        result = MarketAssetsListResponse(total=total, assets=assets)

        self._cache.set_analytics(cache_key, result.model_dump())
        return result

    # ================================================================
    # GET /market/trends
    # ================================================================

    def get_trends(
        self,
        db: Session,
        asset_name: str,
        period: str = "1M",
    ) -> MarketTrendResponse:
        """
        Compute price trend analysis for a specific asset.
        Periods: 1W, 1M, 3M, 6M, 1Y
        """
        cache_key = f"trend:{asset_name}:{period}"
        cached = self._cache.get_analytics(cache_key)
        if cached:
            cached["cached"] = True
            return MarketTrendResponse(**cached)

        days_map = {"1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365}
        days = days_map.get(period, 30)
        cutoff = datetime.utcnow() - timedelta(days=days)

        rows = (
            db.query(MarketData)
            .filter(
                MarketData.asset_name == asset_name,
                MarketData.timestamp >= cutoff,
            )
            .order_by(MarketData.timestamp.asc())
            .all()
        )

        if not rows:
            # Return empty trend
            return MarketTrendResponse(
                asset_name=asset_name,
                current_price=0.0,
                period=period,
                trend_direction="neutral",
                avg_price=0.0,
                high=0.0,
                low=0.0,
                data_points=[],
            )

        prices = [r.price for r in rows]
        current = prices[-1]
        first = prices[0]
        avg = sum(prices) / len(prices)
        high = max(prices)
        low = min(prices)

        if current > first * 1.02:
            direction = "bullish"
        elif current < first * 0.98:
            direction = "bearish"
        else:
            direction = "neutral"

        data_points = [
            TrendPoint(
                date=r.timestamp.strftime("%Y-%m-%d"),
                price=r.price,
                change_percent=r.change_percent or 0.0,
            )
            for r in rows
        ]

        result = MarketTrendResponse(
            asset_name=asset_name,
            current_price=round(current, 2),
            period=period,
            trend_direction=direction,
            avg_price=round(avg, 2),
            high=round(high, 2),
            low=round(low, 2),
            data_points=data_points,
        )

        self._cache.set_analytics(cache_key, result.model_dump())
        return result

    # ================================================================
    # GET /market/volatility
    # ================================================================

    def get_volatility(self, db: Session) -> VolatilityResponse:
        """
        Calculate market-wide volatility metrics grouped by asset type.
        Uses standard deviation of price changes as volatility proxy.
        """
        cache_key = "volatility:global"
        cached = self._cache.get_analytics(cache_key)
        if cached:
            cached["cached"] = True
            return VolatilityResponse(**cached)

        cutoff = datetime.utcnow() - timedelta(days=30)

        # Fetch recent data grouped by asset type
        rows = (
            db.query(MarketData)
            .filter(MarketData.timestamp >= cutoff)
            .order_by(MarketData.asset_type, MarketData.timestamp)
            .all()
        )

        type_data: Dict[str, List[float]] = {}
        for r in rows:
            changes = type_data.setdefault(r.asset_type, [])
            if r.change_percent is not None:
                changes.append(r.change_percent)

        items: List[VolatilityItem] = []
        all_volatility: List[float] = []

        for asset_type, changes in type_data.items():
            if not changes:
                continue

            vol = self._std_dev(changes)
            avg_change = sum(abs(c) for c in changes) / len(changes) if changes else 0.0
            max_drawdown = abs(min(changes)) if changes else 0.0

            risk_cat = self._volatility_category(vol)
            all_volatility.append(vol)

            items.append(
                VolatilityItem(
                    asset_type=asset_type,
                    volatility_index=round(vol, 4),
                    risk_category=risk_cat,
                    avg_daily_change=round(avg_change, 4),
                    max_drawdown=round(max_drawdown, 4),
                )
            )

        market_vol = sum(all_volatility) / len(all_volatility) if all_volatility else 0.0

        if market_vol < 1.0:
            env = "calm"
        elif market_vol < 2.5:
            env = "moderate"
        elif market_vol < 5.0:
            env = "elevated"
        else:
            env = "stressed"

        result = VolatilityResponse(
            market_volatility=round(market_vol, 4),
            risk_environment=env,
            assets=items,
            computed_at=datetime.utcnow().isoformat(),
        )

        self._cache.set_analytics(cache_key, result.model_dump())
        return result

    # ================================================================
    # GET /market/sector-analysis
    # ================================================================

    def get_sector_analysis(self, db: Session) -> SectorAnalysisResponse:
        """
        Retrieve sector-level performance analysis with sentiment.
        """
        cache_key = "sector:analysis"
        cached = self._cache.get_analytics(cache_key)
        if cached:
            cached["cached"] = True
            return SectorAnalysisResponse(**cached)

        # Latest entry per sector
        latest_sq = (
            db.query(
                SectorData.sector,
                func.max(SectorData.timestamp).label("max_ts"),
            )
            .group_by(SectorData.sector)
            .subquery()
        )

        rows = (
            db.query(SectorData)
            .join(
                latest_sq,
                (SectorData.sector == latest_sq.c.sector)
                & (SectorData.timestamp == latest_sq.c.max_ts),
            )
            .order_by(SectorData.performance.desc())
            .all()
        )

        sectors: List[SectorItem] = []
        for r in rows:
            outlook = "positive" if r.performance > 0.5 else ("negative" if r.performance < -0.5 else "neutral")
            sectors.append(
                SectorItem(
                    sector=r.sector,
                    performance=round(r.performance, 2),
                    weekly_change=round(r.weekly_change or 0.0, 2),
                    monthly_change=round(r.monthly_change or 0.0, 2),
                    market_weight=round(r.market_weight or 0.0, 2),
                    volatility_index=round(r.volatility_index or 0.0, 2),
                    outlook=outlook,
                )
            )

        # Market sentiment from average sector performance
        avg_perf = sum(s.performance for s in sectors) / len(sectors) if sectors else 0.0
        sentiment = "bullish" if avg_perf > 1.0 else ("bearish" if avg_perf < -1.0 else "neutral")

        result = SectorAnalysisResponse(
            total_sectors=len(sectors),
            market_sentiment=sentiment,
            top_performing=sectors[0] if sectors else None,
            worst_performing=sectors[-1] if sectors else None,
            sectors=sectors,
            computed_at=datetime.utcnow().isoformat(),
        )

        self._cache.set_analytics(cache_key, result.model_dump())
        return result

    # ================================================================
    # Helpers
    # ================================================================

    @staticmethod
    def _std_dev(values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    @staticmethod
    def _volatility_category(vol: float) -> str:
        """Map volatility index to a human-readable category."""
        if vol < 1.0:
            return "low"
        elif vol < 3.0:
            return "moderate"
        elif vol < 6.0:
            return "high"
        else:
            return "extreme"
