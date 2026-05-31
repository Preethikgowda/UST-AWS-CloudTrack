"""
IntelliWealth – Customer Schemas
"""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class CustomerCreate(BaseModel):
    """Schema for creating a new customer."""
    name: str = Field(..., min_length=1, max_length=255, description="Full name of the customer")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, max_length=128, description="Account password")
    role: Literal["investor", "advisor", "admin"] = Field(default="investor", description="User role")


class CustomerRegister(BaseModel):
    """Schema for public self-service account registration."""
    name: str = Field(..., min_length=1, max_length=255, description="Full name of the customer")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, max_length=128, description="Account password")


class CustomerUpdate(BaseModel):
    """Schema for updating customer details."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    role: Optional[Literal["investor", "advisor", "admin"]] = None
    is_active: Optional[bool] = None


class CustomerResponse(BaseModel):
    """Schema returned when reading a customer."""
    id: UUID
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerLogin(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str
