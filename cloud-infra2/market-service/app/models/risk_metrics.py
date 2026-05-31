"""
IntelliWealth – Risk Metrics Model
Stores computed risk intelligence per portfolio.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class RiskMetrics(Base):
    """Computed risk intelligence snapshot for a portfolio."""

    __tablename__ = "risk_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    portfolio_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    risk_score = Column(Float, nullable=False, default=0.0)
    risk_level = Column(String(20), nullable=False, default="MODERATE")
    concentration_score = Column(Float, nullable=False, default=0.0)
    diversification_score = Column(Float, nullable=False, default=0.0)
    volatility = Column(Float, nullable=False, default=0.0)
    sector_exposure = Column(JSONB, nullable=True, default=dict)
    recommendations = Column(Text, nullable=True)
    computed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<RiskMetrics(portfolio={self.portfolio_id}, risk={self.risk_level}, score={self.risk_score})>"
