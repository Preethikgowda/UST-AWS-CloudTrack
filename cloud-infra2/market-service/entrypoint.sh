#!/bin/bash
set -e

echo "============================================"
echo "  IntelliWealth – Market Intelligence Service"
echo "  Starting up..."
echo "============================================"

echo "[entrypoint] Waiting for database..."
python -c "from app.database import wait_for_database; wait_for_database()"

# Note: Database migrations are centralized in portfolio-service to avoid conflicts
# on a shared database with separate Alembic tracking. Both services would try to
# create alembic_version tables and track different revision histories in the same DB.
echo "[entrypoint] Migrations managed by portfolio-service (shared database)."

# Seed initial market data if empty
echo "[entrypoint] Checking for seed data..."
python -c "from app.seed import seed_market_data; seed_market_data()" 2>/dev/null || echo "[entrypoint] Seed skipped or already populated."

# Start the service
echo "[entrypoint] Launching uvicorn server..."
exec uvicorn app.main:app \
    --host "${MARKET_SERVICE_HOST:-0.0.0.0}" \
    --port "${MARKET_SERVICE_PORT:-8001}" \
    --log-level "${MARKET_SERVICE_LOG_LEVEL:-info}" \
    --access-log
