"""
IntelliWealth – Market Data Model
Stores point-in-time price snapshots for assets tracked by the platform.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Index, String
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class MarketData(Base):
    """Price snapshot for a tracked market asset."""

    __tablename__ = "market_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    asset_name = Column(String(255), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False)
    previous_price = Column(Float, nullable=True)
    change_percent = Column(Float, nullable=True, default=0.0)
    volume = Column(Float, nullable=True, default=0.0)
    market_cap = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index("ix_market_data_asset_timestamp", "asset_name", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<MarketData(asset={self.asset_name}, price={self.price}, ts={self.timestamp})>"
