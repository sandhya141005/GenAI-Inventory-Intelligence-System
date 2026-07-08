"""initial schema

Revision ID: 20260705_0001
Revises:
Create Date: 2026-07-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260705_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "inventory_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("store_id", sa.String(length=64), nullable=False),
        sa.Column("store_region", sa.String(length=120), nullable=False),
        sa.Column("on_hand_units", sa.Integer(), nullable=False),
        sa.Column("reorder_point", sa.Integer(), nullable=False),
        sa.Column("unit_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inventory_snapshots_category"), "inventory_snapshots", ["category"], unique=False)
    op.create_index(op.f("ix_inventory_snapshots_sku"), "inventory_snapshots", ["sku"], unique=False)
    op.create_index(op.f("ix_inventory_snapshots_snapshot_date"), "inventory_snapshots", ["snapshot_date"], unique=False)
    op.create_index(op.f("ix_inventory_snapshots_store_id"), "inventory_snapshots", ["store_id"], unique=False)
    op.create_index(op.f("ix_inventory_snapshots_store_region"), "inventory_snapshots", ["store_region"], unique=False)

    op.create_table(
        "revenue_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sale_date", sa.Date(), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("store_id", sa.String(length=64), nullable=False),
        sa.Column("channel", sa.String(length=64), nullable=False),
        sa.Column("units_sold", sa.Integer(), nullable=False),
        sa.Column("gross_revenue", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("margin_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_revenue_records_sale_date"), "revenue_records", ["sale_date"], unique=False)
    op.create_index(op.f("ix_revenue_records_sku"), "revenue_records", ["sku"], unique=False)
    op.create_index(op.f("ix_revenue_records_store_id"), "revenue_records", ["store_id"], unique=False)

    op.create_table(
        "stockout_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("store_id", sa.String(length=64), nullable=False),
        sa.Column("estimated_lost_sales", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("duration_hours", sa.Integer(), nullable=False),
        sa.Column("root_cause", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_stockout_events_event_date"), "stockout_events", ["event_date"], unique=False)
    op.create_index(op.f("ix_stockout_events_sku"), "stockout_events", ["sku"], unique=False)
    op.create_index(op.f("ix_stockout_events_store_id"), "stockout_events", ["store_id"], unique=False)

    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_conversations_id"), "conversations", ["id"], unique=False)
    op.create_index(op.f("ix_conversations_user_id"), "conversations", ["user_id"], unique=False)

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("message_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_messages_conversation_id"), "messages", ["conversation_id"], unique=False)
    op.create_index(op.f("ix_messages_id"), "messages", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_messages_id"), table_name="messages")
    op.drop_index(op.f("ix_messages_conversation_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_index(op.f("ix_conversations_user_id"), table_name="conversations")
    op.drop_index(op.f("ix_conversations_id"), table_name="conversations")
    op.drop_table("conversations")
    op.drop_index(op.f("ix_stockout_events_store_id"), table_name="stockout_events")
    op.drop_index(op.f("ix_stockout_events_sku"), table_name="stockout_events")
    op.drop_index(op.f("ix_stockout_events_event_date"), table_name="stockout_events")
    op.drop_table("stockout_events")
    op.drop_index(op.f("ix_revenue_records_store_id"), table_name="revenue_records")
    op.drop_index(op.f("ix_revenue_records_sku"), table_name="revenue_records")
    op.drop_index(op.f("ix_revenue_records_sale_date"), table_name="revenue_records")
    op.drop_table("revenue_records")
    op.drop_index(op.f("ix_inventory_snapshots_store_region"), table_name="inventory_snapshots")
    op.drop_index(op.f("ix_inventory_snapshots_store_id"), table_name="inventory_snapshots")
    op.drop_index(op.f("ix_inventory_snapshots_snapshot_date"), table_name="inventory_snapshots")
    op.drop_index(op.f("ix_inventory_snapshots_sku"), table_name="inventory_snapshots")
    op.drop_index(op.f("ix_inventory_snapshots_category"), table_name="inventory_snapshots")
    op.drop_table("inventory_snapshots")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
