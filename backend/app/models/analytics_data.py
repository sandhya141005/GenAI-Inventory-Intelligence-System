from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column("product_id", primary_key=True)
    sku: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(150))
    category: Mapped[str | None] = mapped_column(String(100), index=True)
    cost: Mapped[Decimal | None] = mapped_column(Numeric)
    price: Mapped[Decimal | None] = mapped_column(Numeric)


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column("store_id", primary_key=True)
    name: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(100))
    region: Mapped[str | None] = mapped_column(String(100), index=True)
    store_type: Mapped[str | None] = mapped_column(String(50))


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column("sale_id", primary_key=True)
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
    quantity: Mapped[int | None] = mapped_column(Integer)

    product: Mapped[Product] = relationship()


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column("transfer_id", primary_key=True)
    from_store_id: Mapped[int | None] = mapped_column("from_store", ForeignKey("stores.store_id"), index=True)
    to_store_id: Mapped[int | None] = mapped_column("to_store", ForeignKey("stores.store_id"), index=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.product_id"), index=True)
    quantity: Mapped[int | None] = mapped_column(Integer)
    transfer_cost: Mapped[Decimal | None] = mapped_column(Numeric)
    transfer_date: Mapped[date | None] = mapped_column(Date)

    product: Mapped[Product] = relationship()
    from_store: Mapped[Store] = relationship(foreign_keys=[from_store_id])
    to_store: Mapped[Store] = relationship(foreign_keys=[to_store_id])
