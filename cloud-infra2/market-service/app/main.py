"""
IntelliWealth – Market Intelligence Service Application Entry Point
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import Base, engine, wait_for_database
from app.routers import health, market

settings = get_settings()

# ---- Logging ----
logging.basicConfig(
    level=getattr(logging, settings.MARKET_SERVICE_LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("intelliwealth.market")


# ---- Lifespan ----
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler – startup and shutdown."""
    logger.info("=" * 60)
    logger.info("  IntelliWealth Market Intelligence Service – Starting")
    logger.info("  Environment: %s", settings.ENVIRONMENT)
    logger.info("  Version: %s", settings.APP_VERSION)
    logger.info("  Redis: %s", settings.REDIS_URL)
    logger.info("=" * 60)

    wait_for_database()

    # Create tables if they don't exist (Alembic handles migrations in production)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified.")

    yield

    logger.info("IntelliWealth Market Intelligence Service – Shutting down.")


# ---- Application ----
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Market intelligence and risk analytics service for the IntelliWealth platform. "
        "Provides market data, trend analysis, volatility metrics, portfolio risk assessment, "
        "and sector performance analysis. NOT a trading service."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Request Logging Middleware ----
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    """Log every request with timing information."""
    start = time.perf_counter()
    response: Response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    logger.info(
        "%s %s → %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.1f}"
    return response


# ---- Global Exception Handler ----
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch unhandled exceptions and return structured error responses."""
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred. Please try again later.",
            "error_type": type(exc).__name__,
            "path": str(request.url.path),
        },
    )


# ---- Routers ----
app.include_router(health.router)
app.include_router(market.router)


@app.get("/", tags=["Root"])
async def root():
    """Service root – redirects to docs."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "endpoints": [
            "/api/v1/market/assets",
            "/api/v1/market/trends",
            "/api/v1/market/volatility",
            "/api/v1/market/risk",
            "/api/v1/market/sector-analysis",
        ],
    }
