"""
IntelliWealth – Auth Router
Handles login and token refresh endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.jwt_handler import create_access_token, create_refresh_token, decode_token, verify_password
from app.database import get_db
from app.schemas.customer import CustomerCreate, CustomerLogin, CustomerRegister, CustomerResponse
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=CustomerResponse, status_code=201, summary="Register a new investor")
async def register(payload: CustomerRegister, db: Session = Depends(get_db)):
    """Create a self-service investor account that can immediately log in."""
    customer = CustomerService.create_customer(
        db,
        CustomerCreate(
            name=payload.name,
            email=payload.email,
            password=payload.password,
            role="investor",
        ),
    )
    return customer


@router.post("/login", summary="Authenticate and obtain tokens")
async def login(payload: CustomerLogin, db: Session = Depends(get_db)):
    """Authenticate a customer and return access + refresh tokens."""
    customer = CustomerService.get_customer_by_email(db, payload.email)

    if not customer or not verify_password(payload.password, customer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    token_data = {"sub": str(customer.id), "email": customer.email, "role": customer.role}

    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer",
        "user": {
            "id": str(customer.id),
            "name": customer.name,
            "email": customer.email,
            "role": customer.role,
            "is_active": customer.is_active,
            "created_at": customer.created_at,
            "updated_at": customer.updated_at,
        },
    }


@router.post("/refresh", summary="Refresh access token")
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access token."""
    payload = decode_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    token_data = {"sub": payload["sub"], "email": payload["email"], "role": payload["role"]}

    return {
        "access_token": create_access_token(token_data),
        "token_type": "bearer",
    }
