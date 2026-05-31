"""
IntelliWealth – Portfolio History Model
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class PortfolioHistory(Base):
    """Point-in-time snapshot of a portfolio's total value."""

    __tablename__ = "portfolio_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    value = Column(Float, nullable=False)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="history")

    def __repr__(self) -> str:
        return f"<PortfolioHistory(id={self.id}, portfolio_id={self.portfolio_id}, value={self.value})>"
