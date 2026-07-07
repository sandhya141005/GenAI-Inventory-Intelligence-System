from datetime import date, timedelta
from decimal import Decimal

from app.models.analytics_data import Product, Sale, Store, WarehouseStock
from app.services.action_engine import InventoryActionInput, SmartInventoryActionEngine
from app.services.donation_service import DonationService


def _input(**overrides):
    defaults = {
        "product_id": 1,
        "product_name": "Test Product",
        "category": "Accessories",
        "current_stock_qty": 12,
        "days_since_last_sold": 20,
        "days_to_expiry": None,
        "price": Decimal("100"),
        "store_city": "Chennai",
        "pickup_location": "Chennai",
    }
    defaults.update(overrides)
    return InventoryActionInput(**defaults)


def test_discard_wins_for_expired_items(db_session):
    suggestion = SmartInventoryActionEngine(db_session).evaluate(
        _input(days_to_expiry=0, days_since_last_sold=120, current_stock_qty=80)
    )

    assert suggestion["action"] == "DISCARD"
    assert suggestion["discount_percent"] is None


def test_donate_wins_before_clearance_for_non_food_slow_movers(db_session):
    suggestion = SmartInventoryActionEngine(db_session).evaluate(
        _input(days_since_last_sold=120, current_stock_qty=50)
    )

    assert suggestion["action"] == "DONATE"
    assert suggestion["suggested_recipient"] == "Sunrise Children's Home"


def test_clearance_uses_highest_expiry_or_slow_mover_discount(db_session):
    suggestion = SmartInventoryActionEngine(db_session).evaluate(
        _input(days_to_expiry=6, days_since_last_sold=70, current_stock_qty=4)
    )

    assert suggestion["action"] == "CLEARANCE_SALE"
    assert suggestion["discount_percent"] == 70


def test_donation_notify_logs_when_smtp_is_not_configured(db_session, monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_USERNAME", raising=False)
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)

    store = Store(name="Chennai Central", city="Chennai", region="South", store_type="store")
    product = Product(
        sku="DONATE-1",
        name="Slow Moving Accessory",
        category="Accessories",
        cost=Decimal("10"),
        price=Decimal("20"),
    )
    db_session.add_all([store, product])
    db_session.commit()

    db_session.add(WarehouseStock(product_id=product.id, quantity=25))
    db_session.add(
        Sale(
            product_id=product.id,
            store_id=store.id,
            sale_date=date.today() - timedelta(days=120),
            quantity=1,
            revenue=Decimal("20"),
        )
    )
    db_session.commit()

    result = DonationService(db_session).notify_orphanages(product.id)

    assert result["status"] == "success"
    assert result["sent"] == 2
    assert all(notification["status"] == "logged" for notification in result["notifications"])
