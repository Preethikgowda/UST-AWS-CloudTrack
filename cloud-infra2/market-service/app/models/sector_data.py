"""
IntelliWealth – Sector Data Model
Tracks sector-level market performance for exposure analysis.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, String
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class SectorData(Base):
    """Sector-level performance record."""

    __tablename__ = "sector_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    sector = Column(String(100), nullable=False, index=True)
    performance = Column(Float, nullable=False, default=0.0)
    weekly_change = Column(Float, nullable=True, default=0.0)
    monthly_change = Column(Float, nullable=True, default=0.0)
    market_weight = Column(Float, nullable=True, default=0.0)
    volatility_index = Column(Float, nullable=True, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<SectorData(sector={self.sector}, performance={self.performance})>"
