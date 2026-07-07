"""smart inventory actions

Revision ID: 20260706_0003
Revises: 20260705_0002
Create Date: 2026-07-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "20260706_0003"
down_revision: str | None = "20260705_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    product_columns = {column["name"] for column in inspector.get_columns("products")}
    if "expiry_date" not in product_columns:
        op.add_column("products", sa.Column("expiry_date", sa.Date(), nullable=True))

    existing_tables = set(inspector.get_table_names())
    if "donations_log" not in existing_tables:
        op.create_table(
            "donations_log",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("orphanage_name", sa.String(length=150), nullable=False),
            sa.Column("orphanage_city", sa.String(length=100), nullable=False),
            sa.Column("orphanage_email", sa.String(length=255), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=False),
            sa.Column("message", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["product_id"], ["products.product_id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing("donations_log", "ix_donations_log_product_id", ["product_id"])


def downgrade() -> None:
    _drop_index_if_exists("donations_log", "ix_donations_log_product_id")
    op.drop_table("donations_log")
    product_columns = {column["name"] for column in inspect(op.get_bind()).get_columns("products")}
    if "expiry_date" in product_columns:
        op.drop_column("products", "expiry_date")


def _create_index_if_missing(table_name: str, index_name: str, columns: list[str]) -> None:
    inspector = inspect(op.get_bind())
    table_columns = {column["name"] for column in inspector.get_columns(table_name)}
    existing_indexes = {index["name"] for index in inspector.get_indexes(table_name)}
    if index_name not in existing_indexes and all(column in table_columns for column in columns):
        op.create_index(index_name, table_name, columns)


def _drop_index_if_exists(table_name: str, index_name: str) -> None:
    inspector = inspect(op.get_bind())
    if table_name not in set(inspector.get_table_names()):
        return
    existing_indexes = {index["name"] for index in inspector.get_indexes(table_name)}
    if index_name in existing_indexes:
        op.drop_index(index_name, table_name=table_name)
