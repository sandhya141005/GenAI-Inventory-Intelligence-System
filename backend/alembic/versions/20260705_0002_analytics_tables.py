"""analytics tables

Revision ID: 20260705_0002
Revises: 20260705_0001
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "20260705_0002"
down_revision: str | None = "20260705_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    existing_tables = set(inspect(op.get_bind()).get_table_names())

    if "products" not in existing_tables:
        op.create_table(
            "products",
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("sku", sa.String(length=50), nullable=True),
            sa.Column("name", sa.String(length=150), nullable=True),
            sa.Column("category", sa.String(length=100), nullable=True),
            sa.Column("cost", sa.Numeric(), nullable=True),
            sa.Column("price", sa.Numeric(), nullable=True),
            sa.PrimaryKeyConstraint("product_id"),
            sa.UniqueConstraint("sku"),
        )
    _create_index_if_missing("products", "ix_products_category", ["category"])

    if "stores" not in existing_tables:
        op.create_table(
            "stores",
            sa.Column("store_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=True),
            sa.Column("city", sa.String(length=100), nullable=True),
            sa.Column("region", sa.String(length=100), nullable=True),
            sa.Column("store_type", sa.String(length=50), nullable=True),
            sa.PrimaryKeyConstraint("store_id"),
        )
    _create_index_if_missing("stores", "ix_stores_region", ["region"])

    if "sales" not in existing_tables:
        op.create_table(
            "sales",
            sa.Column("sale_id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=True),
            sa.Column("store_id", sa.Integer(), nullable=True),
            sa.Column("sale_date", sa.Date(), nullable=True),
            sa.Column("quantity", sa.Integer(), nullable=True),
            sa.Column("revenue", sa.Numeric(), nullable=True),
            sa.PrimaryKeyConstraint("sale_id"),
        )
    _create_index_if_missing("sales", "ix_sales_product_id", ["product_id"])
    _create_index_if_missing("sales", "ix_sales_sale_date", ["sale_date"])
    _create_index_if_missing("sales", "ix_sales_store_id", ["store_id"])

    if "warehouse_stock" not in existing_tables:
        op.create_table(
            "warehouse_stock",
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("quantity", sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint("product_id"),
        )

    if "transfers" not in existing_tables:
        op.create_table(
            "transfers",
            sa.Column("transfer_id", sa.Integer(), nullable=False),
            sa.Column("from_store", sa.Integer(), nullable=True),
            sa.Column("to_store", sa.Integer(), nullable=True),
            sa.Column("product_id", sa.Integer(), nullable=True),
            sa.Column("quantity", sa.Integer(), nullable=True),
            sa.Column("transfer_cost", sa.Numeric(), nullable=True),
            sa.Column("transfer_date", sa.Date(), nullable=True),
            sa.PrimaryKeyConstraint("transfer_id"),
        )
    _create_index_if_missing("transfers", "ix_transfers_from_store", ["from_store"])
    _create_index_if_missing("transfers", "ix_transfers_product_id", ["product_id"])
    _create_index_if_missing("transfers", "ix_transfers_to_store", ["to_store"])


def downgrade() -> None:
    _drop_index_if_exists("transfers", "ix_transfers_to_store")
    _drop_index_if_exists("transfers", "ix_transfers_product_id")
    _drop_index_if_exists("transfers", "ix_transfers_from_store")
    op.drop_table("transfers")
    op.drop_table("warehouse_stock")
    _drop_index_if_exists("sales", "ix_sales_store_id")
    _drop_index_if_exists("sales", "ix_sales_sale_date")
    _drop_index_if_exists("sales", "ix_sales_product_id")
    op.drop_table("sales")
    _drop_index_if_exists("stores", "ix_stores_region")
    op.drop_table("stores")
    _drop_index_if_exists("products", "ix_products_category")
    op.drop_table("products")


def _create_index_if_missing(table_name: str, index_name: str, columns: list[str]) -> None:
    inspector = inspect(op.get_bind())
    table_columns = {column["name"] for column in inspector.get_columns(table_name)}
    existing_indexes = {index["name"] for index in inspector.get_indexes(table_name)}
    if index_name not in existing_indexes and all(column in table_columns for column in columns):
        op.create_index(index_name, table_name, columns)


def _drop_index_if_exists(table_name: str, index_name: str) -> None:
    existing_indexes = {index["name"] for index in inspect(op.get_bind()).get_indexes(table_name)}
    if index_name in existing_indexes:
        op.drop_index(index_name, table_name=table_name)
