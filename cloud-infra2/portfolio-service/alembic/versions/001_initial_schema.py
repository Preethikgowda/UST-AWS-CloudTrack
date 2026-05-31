"""Initial schema – customers, portfolios, assets, transactions, portfolio_history

Revision ID: 001_initial_schema
Revises: None
Create Date: 2026-05-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ---- customers ----
    op.create_table(
        "customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.Text, nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="investor"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("now()")),
    )

    # ---- portfolios ----
    op.create_table(
        "portfolios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False, server_default="Default Portfolio"),
        sa.Column("total_value", sa.Float, nullable=False, server_default=sa.text("0.0")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("now()")),
    )

    # ---- assets ----
    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("asset_name", sa.String(255), nullable=False),
        sa.Column("asset_type", sa.String(50), nullable=False),
        sa.Column("quantity", sa.Float, nullable=False, server_default=sa.text("0.0")),
        sa.Column("purchase_price", sa.Float, nullable=False, server_default=sa.text("0.0")),
        sa.Column("current_value", sa.Float, nullable=False, server_default=sa.text("0.0")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("now()")),
    )

    # ---- transactions ----
    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("timestamp", sa.DateTime, nullable=False, server_default=sa.text("now()")),
    )

    # ---- portfolio_history ----
    op.create_table(
        "portfolio_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("snapshot_date", sa.DateTime, nullable=False, server_default=sa.text("now()"), index=True),
        sa.Column("value", sa.Float, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("portfolio_history")
    op.drop_table("transactions")
    op.drop_table("assets")
    op.drop_table("portfolios")
    op.drop_table("customers")
