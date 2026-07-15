"""realms and rbac

Revision ID: 20260707_0004
Revises: 20260706_0003
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect, text

revision: str = "20260707_0004"
down_revision: str | None = "20260706_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names())

    if "realms" not in existing_tables:
        op.create_table(
            "realms",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("industry_tag", sa.String(length=120), nullable=False),
            sa.Column("join_code", sa.String(length=4), nullable=False),
            sa.Column("owner_user_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_realms_id"), "realms", ["id"], unique=False)
        op.create_index(op.f("ix_realms_join_code"), "realms", ["join_code"], unique=True)
        op.create_index(op.f("ix_realms_owner_user_id"), "realms", ["owner_user_id"], unique=False)

    _add_column_if_missing("users", sa.Column("realm_id", sa.Integer(), nullable=True))
    _add_column_if_missing("users", sa.Column("role", sa.String(length=32), nullable=True))
    _add_column_if_missing("users", sa.Column("assigned_store_id", sa.Integer(), nullable=True))
    _create_index_if_missing("users", "ix_users_realm_id", ["realm_id"])
    _create_index_if_missing("users", "ix_users_assigned_store_id", ["assigned_store_id"])
    _create_fk_if_missing("users", "fk_users_realm_id_realms", ["realm_id"], "realms", ["id"])
    _create_fk_if_missing("users", "fk_users_assigned_store_id_stores", ["assigned_store_id"], "stores", ["store_id"])

    for table in (
        "products",
        "stores",
        "sales",
        "warehouse_stock",
        "transfers",
        "donations_log",
        "inventory_snapshots",
        "revenue_records",
        "stockout_events",
    ):
        if table in set(inspect(op.get_bind()).get_table_names()):
            _add_column_if_missing(table, sa.Column("realm_id", sa.Integer(), nullable=True))
            _create_index_if_missing(table, f"ix_{table}_realm_id", ["realm_id"])
            _create_fk_if_missing(table, f"fk_{table}_realm_id_realms", ["realm_id"], "realms", ["id"])

    conn = op.get_bind()
    default_realm_id = conn.execute(text("select id from realms where join_code = '8341'")).scalar()
    if default_realm_id is None:
        owner_id = conn.execute(text("select id from users order by id limit 1")).scalar()
        default_realm_id = conn.execute(
            text(
                "insert into realms (name, industry_tag, join_code, owner_user_id) "
                "values (:name, :industry_tag, :join_code, :owner_user_id) returning id"
            ),
            {
                "name": "StockLens Demo Realm",
                "industry_tag": "Automotive Parts",
                "join_code": "8341",
                "owner_user_id": owner_id,
            },
        ).scalar_one()

    conn.execute(
        text(
            "update users set realm_id = :realm_id, role = coalesce(role, 'WAREHOUSE_OWNER') "
            "where realm_id is null"
        ),
        {"realm_id": default_realm_id},
    )

    for table in (
        "products",
        "stores",
        "sales",
        "warehouse_stock",
        "transfers",
        "donations_log",
        "inventory_snapshots",
        "revenue_records",
        "stockout_events",
    ):
        if table in set(inspect(op.get_bind()).get_table_names()) and _has_column(table, "realm_id"):
            conn.execute(text(f"update {table} set realm_id = :realm_id where realm_id is null"), {"realm_id": default_realm_id})


def downgrade() -> None:
    for table in (
        "stockout_events",
        "revenue_records",
        "inventory_snapshots",
        "donations_log",
        "transfers",
        "warehouse_stock",
        "sales",
        "stores",
        "products",
    ):
        if _has_column(table, "realm_id"):
            _drop_fk_if_exists(table, f"fk_{table}_realm_id_realms")
            _drop_index_if_exists(table, f"ix_{table}_realm_id")
            op.drop_column(table, "realm_id")

    if _has_column("users", "assigned_store_id"):
        _drop_fk_if_exists("users", "fk_users_assigned_store_id_stores")
        _drop_index_if_exists("users", "ix_users_assigned_store_id")
        op.drop_column("users", "assigned_store_id")
    if _has_column("users", "role"):
        op.drop_column("users", "role")
    if _has_column("users", "realm_id"):
        _drop_fk_if_exists("users", "fk_users_realm_id_realms")
        _drop_index_if_exists("users", "ix_users_realm_id")
        op.drop_column("users", "realm_id")

    if "realms" in set(inspect(op.get_bind()).get_table_names()):
        op.drop_index(op.f("ix_realms_owner_user_id"), table_name="realms")
        op.drop_index(op.f("ix_realms_join_code"), table_name="realms")
        op.drop_index(op.f("ix_realms_id"), table_name="realms")
        op.drop_table("realms")


def _has_column(table_name: str, column_name: str) -> bool:
    return column_name in {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if table_name in set(inspect(op.get_bind()).get_table_names()) and not _has_column(table_name, column.name):
        op.add_column(table_name, column)


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
