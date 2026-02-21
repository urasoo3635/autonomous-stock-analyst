"""initial tables

Revision ID: 001
Revises: 
Create Date: 2026-02-20 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # stocks テーブル
    op.create_table(
        "stocks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticker", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("sector", sa.String(length=100), nullable=True),
        sa.Column("market", sa.String(length=50), nullable=True),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_stocks_ticker", "stocks", ["ticker"], unique=True)

    # stock_prices テーブル
    op.create_table(
        "stock_prices",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("stock_id", sa.Integer(), nullable=False),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("open", sa.Numeric(12, 4), nullable=False),
        sa.Column("high", sa.Numeric(12, 4), nullable=False),
        sa.Column("low", sa.Numeric(12, 4), nullable=False),
        sa.Column("close", sa.Numeric(12, 4), nullable=False),
        sa.Column("volume", sa.BigInteger(), nullable=False),
        sa.Column("adjusted_close", sa.Numeric(12, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["stock_id"], ["stocks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stock_id", "price_date", name="uq_stock_price_date"),
    )
    op.create_index("ix_stock_prices_stock_date", "stock_prices", ["stock_id", "price_date"])

    # macro_indicators テーブル
    op.create_table(
        "macro_indicators",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("series_id", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("indicator_date", sa.Date(), nullable=False),
        sa.Column("value", sa.Numeric(18, 6), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("series_id", "indicator_date", name="uq_macro_series_date"),
    )
    op.create_index("ix_macro_series_date", "macro_indicators", ["series_id", "indicator_date"])
    op.create_index("ix_macro_series_id", "macro_indicators", ["series_id"])


def downgrade() -> None:
    op.drop_table("macro_indicators")
    op.drop_table("stock_prices")
    op.drop_table("stocks")
