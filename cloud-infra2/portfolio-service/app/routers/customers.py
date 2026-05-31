"""
IntelliWealth – Customer Router
API endpoints for customer management.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin
from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/api/v1/customers", tags=["Customers"])


@router.post("", response_model=CustomerResponse, status_code=201, summary="Create a new customer")
async def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(require_admin),
):
    """Create a platform customer. Restricted to admins because role is configurable."""
    customer = CustomerService.create_customer(db, payload)
    return customer


@router.get("/{customer_id}", response_model=CustomerResponse, summary="Get customer by ID")
async def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user),
):
    """Retrieve a customer's details by their ID."""
    return CustomerService.get_customer(db, customer_id)


@router.put("/{customer_id}", response_model=CustomerResponse, summary="Update customer")
async def update_customer(
    customer_id: UUID,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user),
):
    """Update a customer's profile details."""
    if current_user.role != "admin" and current_user.id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile",
        )

    if current_user.role != "admin" and (payload.role is not None or payload.is_active is not None):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can change role or active status",
        )

    return CustomerService.update_customer(db, customer_id, payload)


@router.get("", response_model=List[CustomerResponse], summary="List all customers")
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: Customer = Depends(require_admin),
):
    """List all customers (admin only)."""
    return CustomerService.list_customers(db, skip, limit)
