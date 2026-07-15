"""store scope donation logs

Revision ID: 20260709_0005
Revises: 20260708_0005
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "20260709_0005"
down_revision: str | None = "20260708_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if "donations_log" not in set(inspect(op.get_bind()).get_table_names()):
        return
    if not _has_column("donations_log", "store_id"):
        op.add_column("donations_log", sa.Column("store_id", sa.Integer(), nullable=True))
    _create_index_if_missing("donations_log", "ix_donations_log_store_id", ["store_id"])
    _create_fk_if_missing("donations_log", "fk_donations_log_store_id_stores", ["store_id"], "stores", ["store_id"])


def downgrade() -> None:
    if "donations_log" not in set(inspect(op.get_bind()).get_table_names()):
        return
    if _has_column("donations_log", "store_id"):
        _drop_fk_if_exists("donations_log", "fk_donations_log_store_id_stores")
        _drop_index_if_exists("donations_log", "ix_donations_log_store_id")
        op.drop_column("donations_log", "store_id")


def _has_column(table_name: str, column_name: str) -> bool:
    return column_name in {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def _create_index_if_missing(table_name: str, index_name: str, columns: list[str]) -> None:
    existing_indexes = {index["name"] for index in inspect(op.get_bind()).get_indexes(table_name)}
    if index_name not in existing_indexes:
        op.create_index(index_name, table_name, columns)


def _drop_index_if_exists(table_name: str, index_name: str) -> None:
    existing_indexes = {index["name"] for index in inspect(op.get_bind()).get_indexes(table_name)}
    if index_name in existing_indexes:
        op.drop_index(index_name, table_name=table_name)


def _create_fk_if_missing(
    table_name: str,
    constraint_name: str,
    local_cols: list[str],
    remote_table: str,
    remote_cols: list[str],
) -> None:
    existing = {fk["name"] for fk in inspect(op.get_bind()).get_foreign_keys(table_name)}
    if constraint_name not in existing:
        op.create_foreign_key(constraint_name, table_name, remote_table, local_cols, remote_cols)


def _drop_fk_if_exists(table_name: str, constraint_name: str) -> None:
    existing = {fk["name"] for fk in inspect(op.get_bind()).get_foreign_keys(table_name)}
    if constraint_name in existing:
        op.drop_constraint(constraint_name, table_name, type_="foreignkey")
