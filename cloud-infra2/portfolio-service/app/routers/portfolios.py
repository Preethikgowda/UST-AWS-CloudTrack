"""
IntelliWealth – Portfolio Router
API endpoints for portfolio, asset, allocation, and history management.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.asset import Asset
from app.models.customer import Customer
from app.models.portfolio import Portfolio
from app.schemas.asset import AssetCreate, AssetResponse, AssetUpdate
from app.schemas.portfolio import AllocationResponse, PortfolioCreate, PortfolioResponse
from app.schemas.portfolio_history import PortfolioHistoryResponse
from app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/api/v1/portfolio", tags=["Portfolio"])


# ---- Portfolio ----

@router.post("", response_model=PortfolioResponse, status_code=201, summary="Create a portfolio")
async def create_portfolio(
    payload: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user),
):
    """Create a new investment portfolio for a customer."""
    if current_user.role != "admin" and payload.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create portfolios for your own account",
        )
    return PortfolioService.create_portfolio(db, payload)


@router.get("", response_model=List[PortfolioResponse], summary="List current user's portfolios")
async def list_portfolios(
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user),
):
    """List portfolios owned by the current user."""
    return PortfolioService.get_portfolios_by_customer(db, current_user.id)


# ---- Asset Operations ----

@router.post("/add-asset", response_model=AssetResponse, status_code=201, summary="Add asset to portfolio")
async def add_asset(
    payload: AssetCreate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user),
):
    """Add a new asset holding to a portfolio."""
    portfolio = db.query(Portfolio).filter(Portfolio.id == payload.portfolio_id).first()
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {payload.portfolio_id} not found",
        )
    if current_user.role != "admin" and portfolio.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add assets to your own portfolios",
        )
    return PortfolioService.add_asset(db, payload)


@router.put("/update-asset/{asset_id}", response_model=AssetResponse, summary="Update an asset")
async def update_asset(
    asset_id: UUID,
    payload: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user),
):
    """Update an existing asset's details."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset {asset_id} not found",
        )
    portfolio = db.query(Portfolio).filter(Portfolio.id == asset.portfolio_id).first()
    if portfolio and current_user.role != "admin" and portfolio.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update assets in your own portfolios",
        )
    return PortfolioService.update_asset(db, asset_id, payload)


@router.delete("/remove-asset/{asset_id}", summary="Remove an asset")
async def remove_asset(
    asset_id: UUID,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user),
):
    """Remove an asset from a portfolio."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset {asset_id} not found",
        )
    portfolio = db.query(Portfolio).filter(Portfolio.id == asset.portfolio_id).first()
    if portfolio and current_user.role != "admin" and portfolio.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only remove assets from your own portfolios",
        )
    return PortfolioService.remove_asset(db, asset_id)


# ---- Allocation ----

@router.get("/allocation/{portfolio_id}", response_model=AllocationResponse, summary="Get allocation breakdown")
async def get_allocation(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user),
):
    """Get portfolio allocation breakdown by asset type."""
    portfolio = PortfolioService.get_portfolio(db, portfolio_id)
    if current_user.role != "admin" and portfolio.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only inspect your own portfolios",
        )
    return PortfolioService.get_allocation(db, portfolio_id)


# ---- History ----

@router.post("/history/{portfolio_id}/snapshot", response_model=PortfolioHistoryResponse, status_code=201, summary="Record portfolio snapshot")
async def record_snapshot(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user),
):
    """Record the current portfolio value in the history table."""
    portfolio = PortfolioService.get_portfolio(db, portfolio_id)
    if current_user.role != "admin" and portfolio.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only snapshot your own portfolios",
        )
    return PortfolioService.record_snapshot(db, portfolio_id)


@router.get("/history/{portfolio_id}", response_model=List[PortfolioHistoryResponse], summary="Get portfolio history")
async def get_history(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user),
):
    """Retrieve portfolio value history snapshots."""
    portfolio = PortfolioService.get_portfolio(db, portfolio_id)
    if current_user.role != "admin" and portfolio.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only inspect your own portfolios",
        )
    return PortfolioService.get_history(db, portfolio_id)


@router.get("/{portfolio_id}", response_model=PortfolioResponse, summary="Get portfolio by ID")
async def get_portfolio(
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    current_user: Customer = Depends(get_current_user),
):
    """Retrieve a specific portfolio with its assets."""
    portfolio = PortfolioService.get_portfolio(db, portfolio_id)
    if current_user.role != "admin" and portfolio.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own portfolios",
        )
    return portfolio
