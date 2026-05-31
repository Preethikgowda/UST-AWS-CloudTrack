"""
IntelliWealth – Market Data Schemas
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MarketAssetResponse(BaseModel):
    """Single market asset with current pricing."""
    id: UUID
    asset_name: str
    asset_type: str
    price: float
    previous_price: Optional[float] = None
    change_percent: Optional[float] = 0.0
    volume: Optional[float] = 0.0
    market_cap: Optional[float] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class MarketAssetsListResponse(BaseModel):
    """Paginated list of market assets."""
    total: int
    assets: List[MarketAssetResponse]
    cached: bool = False


class TrendPoint(BaseModel):
    """Single data point in a trend series."""
    date: str
    price: float
    change_percent: float


class MarketTrendResponse(BaseModel):
    """Trend analysis for an asset or the overall market."""
    asset_name: str
    current_price: float
    period: str
    trend_direction: str  # bullish, bearish, neutral
    avg_price: float
    high: float
    low: float
    data_points: List[TrendPoint]
    cached: bool = False


class VolatilityItem(BaseModel):
    """Volatility metrics for a single asset type."""
    asset_type: str
    volatility_index: float
    risk_category: str  # low, moderate, high, extreme
    avg_daily_change: float
    max_drawdown: float


class VolatilityResponse(BaseModel):
    """Market-wide volatility analysis."""
    market_volatility: float
    risk_environment: str  # calm, moderate, elevated, stressed
    assets: List[VolatilityItem]
    computed_at: str
    cached: bool = False
