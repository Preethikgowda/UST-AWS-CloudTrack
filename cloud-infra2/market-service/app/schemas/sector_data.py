"""
IntelliWealth – Sector Data Schemas
"""

from typing import List, Optional

from pydantic import BaseModel


class SectorItem(BaseModel):
    """Performance data for a single sector."""
    sector: str
    performance: float
    weekly_change: Optional[float] = 0.0
    monthly_change: Optional[float] = 0.0
    market_weight: Optional[float] = 0.0
    volatility_index: Optional[float] = 0.0
    outlook: str  # positive, neutral, negative


class SectorAnalysisResponse(BaseModel):
    """Complete sector analysis report."""
    total_sectors: int
    market_sentiment: str  # bullish, neutral, bearish
    top_performing: Optional[SectorItem] = None
    worst_performing: Optional[SectorItem] = None
    sectors: List[SectorItem]
    computed_at: str
    cached: bool = False
