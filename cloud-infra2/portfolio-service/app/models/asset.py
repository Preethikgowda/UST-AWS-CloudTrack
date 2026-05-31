"""
IntelliWealth – Asset Model
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Asset(Base):
    """Represents an individual asset holding within a portfolio."""

    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_name = Column(String(255), nullable=False)
    asset_type = Column(String(50), nullable=False)  # stocks, gold, mutual_funds, crypto, bonds, cash
    quantity = Column(Float, nullable=False, default=0.0)
    purchase_price = Column(Float, nullable=False, default=0.0)
    current_value = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="assets")
    transactions = relationship("Transaction", back_populates="asset", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Asset(id={self.id}, name={self.asset_name}, type={self.asset_type})>"
