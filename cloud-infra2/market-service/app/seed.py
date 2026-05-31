"""
IntelliWealth – Market Data Seed Script
Populates initial market data and sector data for development.
"""

import logging
import random
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models.market_data import MarketData
from app.models.sector_data import SectorData

logger = logging.getLogger("intelliwealth.seed")

# ---- Seed Asset Definitions ----
SEED_ASSETS = [
    # Stocks
    {"asset_name": "AAPL", "asset_type": "stocks", "base_price": 178.0},
    {"asset_name": "MSFT", "asset_type": "stocks", "base_price": 420.0},
    {"asset_name": "GOOGL", "asset_type": "stocks", "base_price": 175.0},
    {"asset_name": "AMZN", "asset_type": "stocks", "base_price": 185.0},
    {"asset_name": "TSLA", "asset_type": "stocks", "base_price": 245.0},
    {"asset_name": "NVDA", "asset_type": "stocks", "base_price": 890.0},
    {"asset_name": "META", "asset_type": "stocks", "base_price": 510.0},
    # Gold
    {"asset_name": "GOLD", "asset_type": "gold", "base_price": 2380.0},
    {"asset_name": "GLD ETF", "asset_type": "gold", "base_price": 220.0},
    # Crypto
    {"asset_name": "BTC", "asset_type": "crypto", "base_price": 68500.0},
    {"asset_name": "ETH", "asset_type": "crypto", "base_price": 3750.0},
    {"asset_name": "SOL", "asset_type": "crypto", "base_price": 172.0},
    # Bonds
    {"asset_name": "US Treasury 10Y", "asset_type": "bonds", "base_price": 96.5},
    {"asset_name": "Vanguard Bond ETF", "asset_type": "bonds", "base_price": 82.0},
    {"asset_name": "iShares Corp Bond", "asset_type": "bonds", "base_price": 108.0},
    # Mutual Funds
    {"asset_name": "HDFC Equity Fund", "asset_type": "mutual_funds", "base_price": 48.0},
    {"asset_name": "Vanguard 500 Index", "asset_type": "mutual_funds", "base_price": 520.0},
    {"asset_name": "Fidelity Growth", "asset_type": "mutual_funds", "base_price": 195.0},
    # Cash
    {"asset_name": "USD Money Market", "asset_type": "cash", "base_price": 1.0},
]

# ---- Volatility per asset type (daily % std dev) ----
VOLATILITY = {
    "stocks": 1.8,
    "gold": 0.9,
    "crypto": 4.5,
    "bonds": 0.3,
    "mutual_funds": 1.2,
    "cash": 0.01,
}

# ---- Sector Definitions ----
SEED_SECTORS = [
    {"sector": "Technology", "performance": 2.8, "weekly": 1.2, "monthly": 4.5, "weight": 28.0, "vol": 2.1},
    {"sector": "Healthcare", "performance": 1.5, "weekly": 0.6, "monthly": 2.8, "weight": 14.0, "vol": 1.5},
    {"sector": "Financial Services", "performance": 1.2, "weekly": 0.8, "monthly": 3.2, "weight": 12.0, "vol": 1.8},
    {"sector": "Consumer Cyclical", "performance": 0.8, "weekly": 0.3, "monthly": 1.5, "weight": 10.0, "vol": 2.0},
    {"sector": "Energy", "performance": -0.5, "weekly": -0.8, "monthly": -2.1, "weight": 8.0, "vol": 3.2},
    {"sector": "Industrials", "performance": 0.6, "weekly": 0.4, "monthly": 1.8, "weight": 9.0, "vol": 1.6},
    {"sector": "Real Estate", "performance": -1.2, "weekly": -0.5, "monthly": -3.5, "weight": 5.0, "vol": 2.5},
    {"sector": "Utilities", "performance": 0.3, "weekly": 0.1, "monthly": 0.8, "weight": 4.0, "vol": 0.9},
    {"sector": "Materials", "performance": 0.9, "weekly": 0.5, "monthly": 2.0, "weight": 5.0, "vol": 2.2},
    {"sector": "Communication Services", "performance": 1.8, "weekly": 0.9, "monthly": 3.8, "weight": 5.0, "vol": 1.9},
]


def seed_market_data() -> None:
    """Generate 90 days of historical market data and current sector data."""
    db = SessionLocal()
    try:
        # Check if data already exists
        existing = db.query(MarketData).first()
        if existing:
            logger.info("Market data already seeded. Skipping.")
            return

        logger.info("Seeding market data (90 days × %d assets)...", len(SEED_ASSETS))
        now = datetime.utcnow()
        records = []

        for asset_def in SEED_ASSETS:
            price = asset_def["base_price"]
            vol = VOLATILITY.get(asset_def["asset_type"], 1.0)

            for day_offset in range(90, -1, -1):
                ts = now - timedelta(days=day_offset)
                # Simulate daily price movement
                change_pct = random.gauss(0.02, vol)  # slight upward bias
                prev_price = price
                price = max(price * (1 + change_pct / 100.0), 0.01)

                records.append(
                    MarketData(
                        asset_name=asset_def["asset_name"],
                        asset_type=asset_def["asset_type"],
                        price=round(price, 2),
                        previous_price=round(prev_price, 2),
                        change_percent=round(change_pct, 4),
                        volume=round(random.uniform(100000, 50000000), 0),
                        market_cap=round(price * random.uniform(1e8, 1e10), 0) if asset_def["asset_type"] != "cash" else None,
                        timestamp=ts,
                    )
                )

        db.bulk_save_objects(records)
        logger.info("Inserted %d market data records.", len(records))

        # Seed sector data
        logger.info("Seeding sector data (%d sectors)...", len(SEED_SECTORS))
        for s in SEED_SECTORS:
            db.add(
                SectorData(
                    sector=s["sector"],
                    performance=s["performance"],
                    weekly_change=s["weekly"],
                    monthly_change=s["monthly"],
                    market_weight=s["weight"],
                    volatility_index=s["vol"],
                    timestamp=now,
                )
            )

        db.commit()
        logger.info("Market data seeding complete.")

    except Exception as exc:
        db.rollback()
        logger.error("Seed failed: %s", exc, exc_info=True)
    finally:
        db.close()
