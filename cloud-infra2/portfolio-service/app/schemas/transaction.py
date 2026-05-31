"""
IntelliWealth – Transaction Schemas
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TransactionResponse(BaseModel):
    """Schema returned when reading a transaction."""
    id: UUID
    asset_id: UUID
    type: str
    amount: float
    timestamp: datetime

    model_config = {"from_attributes": True}
