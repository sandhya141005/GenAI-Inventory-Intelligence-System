from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.business_data import InventorySnapshot, RevenueRecord, StockoutEvent


def seed() -> None:
    db = SessionLocal()
    try:
        if db.scalar(select(InventorySnapshot.id).limit(1)):
            print("Mock business data already exists; skipping.")
            return

        today = date.today()
        skus = [
            ("SKU-PC-100", "Hydrating Shampoo 400ml", "Personal Care", Decimal("4.20")),
            ("SKU-EL-220", "Bluetooth Earbuds", "Electronics", Decimal("18.50")),
            ("SKU-AP-410", "Linen Shirt", "Apparel", Decimal("11.25")),
        ]
        stores = [("ST-001", "North"), ("ST-014", "South"), ("ST-022", "West")]

        for sku, name, category, cost in skus:
            for store_id, region in stores:
                db.add(
                    InventorySnapshot(
                        snapshot_date=today,
                        sku=sku,
                        product_name=name,
                        category=category,
                        store_id=store_id,
                        store_region=region,
                        on_hand_units=42 if region == "North" else 125,
                        reorder_point=60,
                        unit_cost=cost,
                    )
                )

        for day_offset in range(7):
            for sku, _name, _category, _cost in skus:
                db.add(
                    RevenueRecord(
                        sale_date=today - timedelta(days=day_offset),
                        sku=sku,
                        store_id="ST-001",
                        channel="store",
                        units_sold=28 + day_offset,
                        gross_revenue=Decimal("2400.00") + Decimal(day_offset * 130),
                        margin_amount=Decimal("730.00") + Decimal(day_offset * 25),
                    )
                )

        db.add_all(
            [
                StockoutEvent(
                    event_date=today - timedelta(days=1),
                    sku="SKU-PC-100",
                    store_id="ST-001",
                    estimated_lost_sales=Decimal("12400.00"),
                    duration_hours=18,
                    root_cause="Demand spike exceeded replenishment threshold.",
                ),
                StockoutEvent(
                    event_date=today - timedelta(days=2),
                    sku="SKU-EL-220",
                    store_id="ST-022",
                    estimated_lost_sales=Decimal("8900.00"),
                    duration_hours=9,
                    root_cause="Late supplier delivery.",
                ),
            ]
        )
        db.commit()
        print("Seeded mock business data.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
