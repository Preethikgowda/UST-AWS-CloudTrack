"""
IntelliWealth – Customer Model
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Customer(Base):
    """Represents a platform customer / investor."""

    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(Text, nullable=False)
    role = Column(String(50), nullable=False, default="investor")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    portfolios = relationship("Portfolio", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, name={self.name}, email={self.email})>"
