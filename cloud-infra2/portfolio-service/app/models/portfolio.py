"""
IntelliWealth – Portfolio Model
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Portfolio(Base):
    """Represents an investment portfolio owned by a customer."""

    __tablename__ = "portfolios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, default="Default Portfolio")
    total_value = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="portfolios")
    assets = relationship("Asset", back_populates="portfolio", cascade="all, delete-orphan")
    history = relationship("PortfolioHistory", back_populates="portfolio", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Portfolio(id={self.id}, customer_id={self.customer_id}, total_value={self.total_value})>"
