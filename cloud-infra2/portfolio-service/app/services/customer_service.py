"""
IntelliWealth – Customer Service
Business logic for customer CRUD operations.
"""

from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.jwt_handler import hash_password
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    """Encapsulates all customer-related business logic."""

    @staticmethod
    def create_customer(db: Session, payload: CustomerCreate) -> Customer:
        """Register a new customer."""
        existing = db.query(Customer).filter(Customer.email == payload.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Customer with email '{payload.email}' already exists",
            )

        customer = Customer(
            name=payload.name,
            email=payload.email,
            hashed_password=hash_password(payload.password),
            role=payload.role,
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def get_customer(db: Session, customer_id: UUID) -> Customer:
        """Retrieve a single customer by ID."""
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer {customer_id} not found",
            )
        return customer

    @staticmethod
    def update_customer(db: Session, customer_id: UUID, payload: CustomerUpdate) -> Customer:
        """Update an existing customer's details."""
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer {customer_id} not found",
            )

        update_data = payload.model_dump(exclude_unset=True)
        if "email" in update_data:
            existing = db.query(Customer).filter(Customer.email == update_data["email"], Customer.id != customer_id).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Customer with email '{update_data['email']}' already exists",
                )

        for field, value in update_data.items():
            setattr(customer, field, value)

        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def list_customers(db: Session, skip: int = 0, limit: int = 100):
        """List all customers with pagination."""
        return db.query(Customer).offset(skip).limit(limit).all()

    @staticmethod
    def get_customer_by_email(db: Session, email: str) -> Optional[Customer]:
        """Lookup a customer by email."""
        return db.query(Customer).filter(Customer.email == email).first()
