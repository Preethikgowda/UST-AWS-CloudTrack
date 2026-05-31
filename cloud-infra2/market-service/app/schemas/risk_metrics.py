"""
IntelliWealth – Risk Metrics Schemas
"""

from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class ConcentrationBreakdown(BaseModel):
    """Concentration analysis by asset type."""
    asset_type: str
    allocation_percent: float
    risk_contribution: str  # low, moderate, high


class RiskAssessmentResponse(BaseModel):
    """Complete risk intelligence report for a portfolio."""
    portfolio_id: UUID
    risk_score: float
    risk_level: str  # LOW, MODERATE, HIGH, CRITICAL
    concentration_score: float
    diversification_score: float
    volatility: float
    sector_exposure: Dict[str, float]
    concentration_breakdown: List[ConcentrationBreakdown]
    recommendations: List[str]
    computed_at: str
    cached: bool = False
