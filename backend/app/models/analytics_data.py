from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column("product_id", primary_key=True)
    realm_id: Mapped[int | None] = mapped_column(ForeignKey("realms.id"), index=True, nullable=True)
    sku: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(150))
    category: Mapped[str | None] = mapped_column(String(100), index=True)
    cost: Mapped[Decimal | None] = mapped_column(Numeric)
    price: Mapped[Decimal | None] = mapped_column(Numeric)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class DonationLog(Base):
    __tablename__ = "donations_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    realm_id: Mapped[int | None] = mapped_column(ForeignKey("realms.id"), index=True, nullable=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), index=True)
    orphanage_name: Mapped[str] = mapped_column(String(150), nullable=False)
    orphanage_city: Mapped[str] = mapped_column(String(100), nullable=False)
    orphanage_email: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product: Mapped[Product] = relationship()


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column("store_id", primary_key=True)
    realm_id: Mapped[int | None] = mapped_column(ForeignKey("realms.id"), index=True, nullable=True)
    name: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(100))
    region: Mapped[str | None] = mapped_column(String(100), index=True)
    store_type: Mapped[str | None] = mapped_column(String(50))


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column("sale_id", primary_key=True)
    realm_id: Mapped[int | None] = mapped_column(ForeignKey("realms.id"), index=True, nullable=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.product_id"), index=True)
    store_id: Mapped[int | None] = mapped_column(ForeignKey("stores.store_id"), index=True)
    sale_date: Mapped[date | None] = mapped_column(Date, index=True)
    quantity: Mapped[int | None] = mapped_column(Integer)
    revenue: Mapped[Decimal | None] = mapped_column(Numeric)

    product: Mapped[Product] = relationship()
    store: Mapped[Store] = relationship()


class WarehouseStock(Base):
    __tablename__ = "warehouse_stock"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), primary_key=True)
    realm_id: Mapped[int | None] = mapped_column(ForeignKey("realms.id"), index=True, nullable=True)
    quantity: Mapped[int | None] = mapped_column(Integer)

    product: Mapped[Product] = relationship()


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column("transfer_id", primary_key=True)
    realm_id: Mapped[int | None] = mapped_column(ForeignKey("realms.id"), index=True, nullable=True)
    from_store_id: Mapped[int | None] = mapped_column("from_store", ForeignKey("stores.store_id"), index=True)
    to_store_id: Mapped[int | None] = mapped_column("to_store", ForeignKey("stores.store_id"), index=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.product_id"), index=True)
    quantity: Mapped[int | None] = mapped_column(Integer)
    transfer_cost: Mapped[Decimal | None] = mapped_column(Numeric)
    transfer_date: Mapped[date | None] = mapped_column(Date)

    product: Mapped[Product] = relationship()
    from_store: Mapped[Store] = relationship(foreign_keys=[from_store_id])
    to_store: Mapped[Store] = relationship(foreign_keys=[to_store_id])
