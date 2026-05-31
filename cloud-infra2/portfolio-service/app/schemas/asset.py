"""
IntelliWealth – Asset Schemas
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AssetType(str, Enum):
    """Allowed asset types."""
    STOCKS = "stocks"
    GOLD = "gold"
    MUTUAL_FUNDS = "mutual_funds"
    CRYPTO = "crypto"
    BONDS = "bonds"
    CASH = "cash"


class AssetCreate(BaseModel):
    """Schema for adding a new asset to a portfolio."""
    portfolio_id: UUID = Field(..., description="Target portfolio ID")
    asset_name: str = Field(..., min_length=1, max_length=255, description="Name of the asset")
    asset_type: AssetType = Field(..., description="Type of asset")
    quantity: float = Field(..., gt=0, description="Quantity held")
    purchase_price: float = Field(..., ge=0, description="Purchase price per unit")


class AssetUpdate(BaseModel):
    """Schema for updating an existing asset."""
    asset_name: Optional[str] = Field(None, min_length=1, max_length=255)
    asset_type: Optional[AssetType] = None
    quantity: Optional[float] = Field(None, gt=0)
    purchase_price: Optional[float] = Field(None, ge=0)
    current_value: Optional[float] = Field(None, ge=0)


class AssetResponse(BaseModel):
    """Schema returned when reading an asset."""
    id: UUID
    portfolio_id: UUID
    asset_name: str
    asset_type: str
    quantity: float
    purchase_price: float
    current_value: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
