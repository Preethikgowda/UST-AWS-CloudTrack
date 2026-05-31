"""
IntelliWealth – Portfolio Service Application Entry Point
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine, wait_for_database
from app.routers import auth, customers, health, portfolios

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.PORTFOLIO_SERVICE_LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("intelliwealth")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler – startup and shutdown."""
    logger.info("=" * 60)
    logger.info("  IntelliWealth Portfolio Service – Starting")
    logger.info("  Environment: %s", settings.ENVIRONMENT)
    logger.info("  Version: %s", settings.APP_VERSION)
    logger.info("=" * 60)

    wait_for_database()

    # Create tables if they don't exist (Alembic handles migrations in production)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified.")

    yield

    logger.info("IntelliWealth Portfolio Service – Shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise portfolio management and intelligence platform. "
                "Manage customer investment portfolios with full CRUD, "
                "allocation tracking, and historical snapshots.",
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

# ---- Routers ----
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(portfolios.router)


@app.get("/", tags=["Root"])
async def root():
    """Service root – redirects to docs."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
