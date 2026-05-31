"""
IntelliWealth - Database Engine & Session Management
"""

import logging
import sys
import time

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger("intelliwealth.market.database")

engine_options = {"echo": settings.DEBUG}
if settings.ENVIRONMENT == "production":
    engine_options.update(
        {
            "pool_size": 5,
            "max_overflow": 10,
            "pool_pre_ping": True,
            "pool_recycle": 300,
        }
    )

engine = create_engine(settings.DATABASE_URL, **engine_options)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""

    pass


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_database() -> None:
    """Block startup until the database is reachable or exit after retries."""
    delays = [2, 4, 8, 16, 32]

    for attempt, delay in enumerate(delays, start=1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connection verified.")
            return
        except Exception as exc:
            logger.warning(
                "Database connection attempt %s/%s failed: %s. Retrying in %ss.",
                attempt,
                len(delays),
                exc,
                delay,
            )
            time.sleep(delay)

    logger.error("Database connection failed after %s attempts.", len(delays))
    sys.exit(1)
