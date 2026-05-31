"""
IntelliWealth – Portfolio Assets Reader
Reads portfolio asset data from the shared database.
This module allows the market service to query portfolio assets
without a service-to-service HTTP call (shared-DB pattern).
"""

import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Column, Float, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Session

logger = logging.getLogger("intelliwealth.market.portfolio")


def get_portfolio_assets(db: Session, portfolio_id: UUID) -> Optional[List[dict]]:
    """
    Read assets from the portfolio service's 'assets' table.
    Returns a list of dicts with asset_type and current_value,
    or None if the portfolio doesn't exist.
    """
    # First check the portfolio exists
    result = db.execute(
        text("SELECT id FROM portfolios WHERE id = :pid"),
        {"pid": str(portfolio_id)},
    ).fetchone()

    if not result:
        return None

    # Fetch assets
    rows = db.execute(
        text(
            "SELECT asset_type, current_value "
            "FROM assets "
            "WHERE portfolio_id = :pid"
        ),
        {"pid": str(portfolio_id)},
    ).fetchall()

    return [
        {"asset_type": row[0], "current_value": float(row[1])}
        for row in rows
    ]
