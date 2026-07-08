from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class InventorySnapshot(Base):
    __tablename__ = "inventory_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    realm_id: Mapped[int | None] = mapped_column(ForeignKey("realms.id"), index=True, nullable=True)
    snapshot_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    sku: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    store_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    store_region: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    on_hand_units: Mapped[int] = mapped_column(Integer, nullable=False)
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RevenueRecord(Base):
    __tablename__ = "revenue_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    realm_id: Mapped[int | None] = mapped_column(ForeignKey("realms.id"), index=True, nullable=True)
    sale_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    sku: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    store_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    channel: Mapped[str] = mapped_column(String(64), nullable=False)
    units_sold: Mapped[int] = mapped_column(Integer, nullable=False)
    gross_revenue: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    margin_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class StockoutEvent(Base):
    __tablename__ = "stockout_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    realm_id: Mapped[int | None] = mapped_column(ForeignKey("realms.id"), index=True, nullable=True)
    event_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    sku: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    store_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    estimated_lost_sales: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    duration_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
