"""
IntelliWealth – Portfolio Service
Business logic for portfolio, asset, and allocation operations.
"""

from datetime import datetime
from typing import Dict, List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.portfolio import Portfolio
from app.models.portfolio_history import PortfolioHistory
from app.models.transaction import Transaction
from app.schemas.asset import AssetCreate, AssetUpdate
from app.schemas.portfolio import AllocationItem, AllocationResponse, PortfolioCreate


class PortfolioService:
    """Encapsulates all portfolio-related business logic."""

    # ---- Portfolio CRUD ----

    @staticmethod
    def create_portfolio(db: Session, payload: PortfolioCreate) -> Portfolio:
        """Create a new portfolio for a customer."""
        portfolio = Portfolio(
            customer_id=payload.customer_id,
            name=payload.name,
            total_value=0.0,
        )
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
        return portfolio

    @staticmethod
    def get_portfolio(db: Session, portfolio_id: UUID) -> Portfolio:
        """Retrieve a portfolio by ID."""
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio {portfolio_id} not found",
            )
        return portfolio

    @staticmethod
    def get_portfolios_by_customer(db: Session, customer_id: UUID) -> List[Portfolio]:
        """Get all portfolios for a specific customer."""
        return db.query(Portfolio).filter(Portfolio.customer_id == customer_id).all()

    # ---- Asset Operations ----

    @staticmethod
    def add_asset(db: Session, payload: AssetCreate) -> Asset:
        """Add a new asset to a portfolio and record the transaction."""
        # Verify portfolio exists
        portfolio = db.query(Portfolio).filter(Portfolio.id == payload.portfolio_id).first()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio {payload.portfolio_id} not found",
            )

        asset = Asset(
            portfolio_id=payload.portfolio_id,
            asset_name=payload.asset_name,
            asset_type=payload.asset_type.value,
            quantity=payload.quantity,
            purchase_price=payload.purchase_price,
            current_value=payload.quantity * payload.purchase_price,
        )
        db.add(asset)
        db.flush()

        # Record the buy transaction
        transaction = Transaction(
            asset_id=asset.id,
            type="buy",
            amount=payload.quantity * payload.purchase_price,
        )
        db.add(transaction)

        # Recalculate portfolio total
        PortfolioService._recalculate_total(db, portfolio)

        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def update_asset(db: Session, asset_id: UUID, payload: AssetUpdate) -> Asset:
        """Update an existing asset's details."""
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset {asset_id} not found",
            )

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "asset_type" and value is not None:
                setattr(asset, field, value.value if hasattr(value, "value") else value)
            else:
                setattr(asset, field, value)

        # Recalculate current value if quantity or purchase_price changed
        if "quantity" in update_data or "purchase_price" in update_data:
            asset.current_value = asset.quantity * asset.purchase_price

        # Record update transaction
        transaction = Transaction(
            asset_id=asset.id,
            type="update",
            amount=asset.current_value,
        )
        db.add(transaction)

        # Recalculate portfolio total
        portfolio = db.query(Portfolio).filter(Portfolio.id == asset.portfolio_id).first()
        if portfolio:
            PortfolioService._recalculate_total(db, portfolio)

        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def remove_asset(db: Session, asset_id: UUID) -> dict:
        """Remove an asset from a portfolio."""
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset {asset_id} not found",
            )

        portfolio_id = asset.portfolio_id

        # Record sell transaction before deletion
        transaction = Transaction(
            asset_id=asset.id,
            type="sell",
            amount=asset.current_value,
        )
        db.add(transaction)
        db.flush()

        # Delete asset (cascade deletes transactions)
        db.delete(asset)

        # Recalculate portfolio total
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if portfolio:
            PortfolioService._recalculate_total(db, portfolio)

        db.commit()
        return {"detail": f"Asset {asset_id} removed successfully"}

    # ---- Allocation ----

    @staticmethod
    def get_allocation(db: Session, portfolio_id: UUID) -> AllocationResponse:
        """Calculate portfolio allocation breakdown by asset type."""
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio {portfolio_id} not found",
            )

        assets = db.query(Asset).filter(Asset.portfolio_id == portfolio_id).all()

        allocation_map: Dict[str, dict] = {}
        total_value = 0.0

        for asset in assets:
            val = asset.current_value or 0.0
            total_value += val
            if asset.asset_type not in allocation_map:
                allocation_map[asset.asset_type] = {"total_value": 0.0, "count": 0}
            allocation_map[asset.asset_type]["total_value"] += val
            allocation_map[asset.asset_type]["count"] += 1

        allocations = []
        for asset_type, info in allocation_map.items():
            percentage = (info["total_value"] / total_value * 100) if total_value > 0 else 0.0
            allocations.append(
                AllocationItem(
                    asset_type=asset_type,
                    total_value=round(info["total_value"], 2),
                    percentage=round(percentage, 2),
                    count=info["count"],
                )
            )

        return AllocationResponse(
            portfolio_id=portfolio_id,
            total_value=round(total_value, 2),
            allocations=allocations,
        )

    # ---- History ----

    @staticmethod
    def get_history(db: Session, portfolio_id: UUID) -> List[PortfolioHistory]:
        """Retrieve portfolio value history snapshots."""
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio {portfolio_id} not found",
            )

        return (
            db.query(PortfolioHistory)
            .filter(PortfolioHistory.portfolio_id == portfolio_id)
            .order_by(PortfolioHistory.snapshot_date.asc())
            .all()
        )

    @staticmethod
    def record_snapshot(db: Session, portfolio_id: UUID) -> PortfolioHistory:
        """Record a point-in-time snapshot of portfolio value."""
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio {portfolio_id} not found",
            )

        snapshot = PortfolioHistory(
            portfolio_id=portfolio_id,
            snapshot_date=datetime.utcnow(),
            value=portfolio.total_value,
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot

    # ---- Internal Helpers ----

    @staticmethod
    def _recalculate_total(db: Session, portfolio: Portfolio) -> None:
        """Recalculate the portfolio total_value from its assets."""
        assets = db.query(Asset).filter(Asset.portfolio_id == portfolio.id).all()
        portfolio.total_value = sum(a.current_value or 0.0 for a in assets)
