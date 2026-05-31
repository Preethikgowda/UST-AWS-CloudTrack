"""
IntelliWealth – Portfolio History Schemas
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PortfolioHistoryResponse(BaseModel):
    """Schema returned when reading a portfolio history snapshot."""
    id: UUID
    portfolio_id: UUID
    snapshot_date: datetime
    value: float

    model_config = {"from_attributes": True}
