"""Market service schema – market_data, sector_data, risk_metrics

Revision ID: 001_market_schema
Revises: None
Create Date: 2026-05-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_market_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID extension (may already exist from portfolio service)
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ---- market_data ----
    op.create_table(
        "market_data",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("asset_name", sa.String(255), nullable=False, index=True),
        sa.Column("asset_type", sa.String(50), nullable=False, index=True),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("previous_price", sa.Float, nullable=True),
        sa.Column("change_percent", sa.Float, nullable=True, server_default=sa.text("0.0")),
        sa.Column("volume", sa.Float, nullable=True, server_default=sa.text("0.0")),
        sa.Column("market_cap", sa.Float, nullable=True),
        sa.Column("timestamp", sa.DateTime, nullable=False, server_default=sa.text("now()"), index=True),
    )
    op.create_index("ix_market_data_asset_timestamp", "market_data", ["asset_name", "timestamp"])

    # ---- sector_data ----
    op.create_table(
        "sector_data",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("sector", sa.String(100), nullable=False, index=True),
        sa.Column("performance", sa.Float, nullable=False, server_default=sa.text("0.0")),
        sa.Column("weekly_change", sa.Float, nullable=True, server_default=sa.text("0.0")),
        sa.Column("monthly_change", sa.Float, nullable=True, server_default=sa.text("0.0")),
        sa.Column("market_weight", sa.Float, nullable=True, server_default=sa.text("0.0")),
        sa.Column("volatility_index", sa.Float, nullable=True, server_default=sa.text("0.0")),
        sa.Column("timestamp", sa.DateTime, nullable=False, server_default=sa.text("now()"), index=True),
    )

    # ---- risk_metrics ----
    op.create_table(
        "risk_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("risk_score", sa.Float, nullable=False, server_default=sa.text("0.0")),
        sa.Column("risk_level", sa.String(20), nullable=False, server_default="MODERATE"),
        sa.Column("concentration_score", sa.Float, nullable=False, server_default=sa.text("0.0")),
        sa.Column("diversification_score", sa.Float, nullable=False, server_default=sa.text("0.0")),
        sa.Column("volatility", sa.Float, nullable=False, server_default=sa.text("0.0")),
        sa.Column("sector_exposure", postgresql.JSONB, nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column("recommendations", sa.Text, nullable=True),
        sa.Column("computed_at", sa.DateTime, nullable=False, server_default=sa.text("now()"), index=True),
    )


def downgrade() -> None:
    op.drop_table("risk_metrics")
    op.drop_table("sector_data")
    op.drop_table("market_data")
