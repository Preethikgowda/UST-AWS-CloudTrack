"""
IntelliWealth – Market Intelligence Router
API endpoints for market data, trends, volatility, risk, and sector analysis.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.market_data import (
    MarketAssetsListResponse,
    MarketTrendResponse,
    VolatilityResponse,
)
from app.schemas.risk_metrics import RiskAssessmentResponse
from app.schemas.sector_data import SectorAnalysisResponse
from app.services.market_service import MarketService
from app.services.risk_engine import RiskEngine

logger = logging.getLogger("intelliwealth.market.router")
router = APIRouter(prefix="/api/v1/market", tags=["Market Intelligence"])

# Service singletons
_market_service = MarketService()
_risk_engine = RiskEngine()


# ================================================================
# GET /market/assets
# ================================================================

@router.get(
    "/assets",
    response_model=MarketAssetsListResponse,
    summary="Get market asset data",
)
async def get_market_assets(
    asset_type: Optional[str] = Query(
        None,
        description="Filter by asset type: stocks, gold, mutual_funds, crypto, bonds, cash",
    ),
    limit: int = Query(50, ge=1, le=200, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
):
    """
    Retrieve latest market data for all tracked assets.
    Supports filtering by asset type and pagination.
    Results are cached in Redis for performance.
    """
    try:
        return _market_service.get_assets(db, asset_type=asset_type, limit=limit, offset=offset)
    except Exception as exc:
        logger.error("Failed to fetch market assets: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve market data",
        )


# ================================================================
# GET /market/trends
# ================================================================

@router.get(
    "/trends",
    response_model=MarketTrendResponse,
    summary="Get asset price trends",
)
async def get_market_trends(
    asset_name: str = Query(..., description="Asset name to analyze"),
    period: str = Query("1M", description="Trend period: 1W, 1M, 3M, 6M, 1Y"),
    db: Session = Depends(get_db),
):
    """
    Compute price trend analysis for a specific asset.
    Returns trend direction, average, high/low, and historical data points.
    """
    valid_periods = {"1W", "1M", "3M", "6M", "1Y"}
    if period not in valid_periods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid period '{period}'. Valid options: {', '.join(valid_periods)}",
        )

    try:
        return _market_service.get_trends(db, asset_name=asset_name, period=period)
    except Exception as exc:
        logger.error("Failed to compute trends for %s: %s", asset_name, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute trend analysis",
        )


# ================================================================
# GET /market/volatility
# ================================================================

@router.get(
    "/volatility",
    response_model=VolatilityResponse,
    summary="Get market volatility metrics",
)
async def get_market_volatility(db: Session = Depends(get_db)):
    """
    Calculate market-wide volatility grouped by asset type.
    Returns volatility index, risk category, and max drawdown per type.
    """
    try:
        return _market_service.get_volatility(db)
    except Exception as exc:
        logger.error("Failed to compute volatility: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute volatility metrics",
        )


# ================================================================
# GET /market/risk
# ================================================================

@router.get(
    "/risk",
    response_model=RiskAssessmentResponse,
    summary="Get portfolio risk assessment",
)
async def get_portfolio_risk(
    portfolio_id: UUID = Query(..., description="Portfolio ID to assess"),
    db: Session = Depends(get_db),
):
    """
    Run comprehensive risk analysis on a portfolio.

    Computes:
    - Portfolio concentration (HHI-based)
    - Sector exposure mapping
    - Diversification score (0–100)
    - Weighted volatility
    - Risk level (LOW / MODERATE / HIGH / CRITICAL)

    Risk rules:
    - Equity > 80% → HIGH risk
    - Gold diversification → reduces risk
    """
    # Fetch portfolio assets from the portfolio service's tables
    # (market-service reads from the shared database)
    from app.models.portfolio_assets import get_portfolio_assets

    assets = get_portfolio_assets(db, portfolio_id)
    if assets is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio {portfolio_id} not found",
        )

    try:
        return _risk_engine.assess_portfolio_risk(db, portfolio_id, assets)
    except Exception as exc:
        logger.error("Risk assessment failed for %s: %s", portfolio_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute risk assessment",
        )


# ================================================================
# GET /market/sector-analysis
# ================================================================

@router.get(
    "/sector-analysis",
    response_model=SectorAnalysisResponse,
    summary="Get sector performance analysis",
)
async def get_sector_analysis(db: Session = Depends(get_db)):
    """
    Retrieve sector-level performance and market sentiment analysis.
    Includes top/worst performing sectors and overall market outlook.
    """
    try:
        return _market_service.get_sector_analysis(db)
    except Exception as exc:
        logger.error("Sector analysis failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute sector analysis",
        )
