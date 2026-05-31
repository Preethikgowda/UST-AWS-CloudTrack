#!/bin/bash
set -e

echo "============================================"
echo "  IntelliWealth – Portfolio Service"
echo "  Starting up..."
echo "============================================"

echo "[entrypoint] Waiting for database..."
python -c "from app.database import wait_for_database; wait_for_database()"

# Run Alembic migrations
echo "[entrypoint] Running database migrations..."
alembic upgrade head

echo "[entrypoint] Migrations complete."

# Seed initial data
echo "[entrypoint] Seeding initial data..."
python -c "from app.seed import seed_admin_user; seed_admin_user()" 2>/dev/null || echo "[entrypoint] Seed skipped or already populated."

# Start the service
echo "[entrypoint] Launching uvicorn server..."
exec uvicorn app.main:app \
    --host "${PORTFOLIO_SERVICE_HOST:-0.0.0.0}" \
    --port "${PORTFOLIO_SERVICE_PORT:-8000}" \
    --log-level "${PORTFOLIO_SERVICE_LOG_LEVEL:-info}" \
    --access-log
