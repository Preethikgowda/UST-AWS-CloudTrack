"""
IntelliWealth – Portfolio Schemas
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.asset import AssetResponse


class PortfolioCreate(BaseModel):
    """Schema for creating a new portfolio."""
    customer_id: UUID = Field(..., description="Owner customer ID")
    name: str = Field(default="Default Portfolio", max_length=255, description="Portfolio name")


class PortfolioResponse(BaseModel):
    """Schema returned when reading a portfolio."""
    id: UUID
    customer_id: UUID
    name: str
    total_value: float
    assets: List[AssetResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AllocationItem(BaseModel):
    """Single item in an allocation breakdown."""
    asset_type: str
    total_value: float
    percentage: float
    count: int


class AllocationResponse(BaseModel):
    """Portfolio allocation breakdown by asset type."""
    portfolio_id: UUID
    total_value: float
    allocations: List[AllocationItem]
