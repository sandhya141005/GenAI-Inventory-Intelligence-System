# seed_demo.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import random
from datetime import date, timedelta
from decimal import Decimal

from app.db.session import SessionLocal
from app.models.analytics_data import Product, Store, InventoryStock, Sale, Transfer
from app.models.user import Realm, User
from sqlalchemy import text

random.seed(42)
db = SessionLocal()

# --- CLEANUP CHOREOGRAPHY ---
# 1. Clear dependent transaction logs first
db.execute(text("DELETE FROM donations_log;"))
# Note: If your engine tracks discards/markdowns in separate log tables, clear them here too:
# db.execute(text("DELETE FROM discards_log;"))
# db.execute(text("DELETE FROM markdowns_log;"))

# 2. Clear core operational items
db.query(Sale).delete()
db.query(Transfer).delete()
db.query(InventoryStock).delete()

# 3. Sever user-to-store relationships, then drop master data safely
db.query(User).update({User.assigned_store_id: None})
db.query(Product).delete()
db.query(Store).delete()
db.commit()

realm = db.query(Realm).filter(Realm.join_code == "8341").first()
if realm is None:
    realm = Realm(name="StockLens Retail Demo", industry_tag="Groceries & Electronics", join_code="8341")
    db.add(realm)
    db.commit()
    db.refresh(realm)

# --- stores: 1 warehouse + 4 retail stores ---
store_defs = [
    ("Warehouse", "Chennai", "South", "warehouse"),
    ("Chennai Central", "Chennai", "South", "retail"),
    ("Ambattur Hub", "Chennai", "South", "retail"),
    ("Coimbatore Store", "Coimbatore", "South", "retail"),
    ("Madurai Store", "Madurai", "South", "retail"),
]
stores = {}
for name, city, region, store_type in store_defs:
    s = Store(name=name, city=city, region=region, store_type=store_type, realm_id=realm.id)
    db.add(s)
    db.flush()
    stores[name] = s

# --- products: groceries + electronics ---
# IMPORTANT: category strings must match ACTION_ENGINE_CONFIG["food_categories"]
# exactly (lowercase, singular where applicable) or _is_food() silently
# returns False and food-only logic (DISCARD, food DONATE, expiry-tier
# CLEARANCE) never fires. Previous seed used "groceries" (plural) which
# never matched "grocery" in the config set.
#
# sku, name, category, cost, price, expiry_offset_days (None = no expiry)
product_defs = [
    ("SKU-1001", "Rice 5kg", "grocery", 180, 240, None),
    ("SKU-1002", "Sugar 1kg", "grocery", 38, 52, None),
    ("SKU-1003", "Milk Packet", "dairy", 22, 30, -2),      # already expired -> DISCARD
    ("SKU-1004", "Tea Powder 250g", "beverages", 90, 130, 90),  # far from expiry -> eligible for DONATE
    ("SKU-1005", "Cooking Oil 1L", "grocery", 110, 150, None),
    ("SKU-1006", "Biscuits Pack", "snacks", 18, 25, 10),   # expiring soon -> CLEARANCE (expiry tier)
    ("SKU-2001", "LED Bulb 9W", "electronics", 60, 99, None),
    ("SKU-2002", "Mobile Charger", "electronics", 150, 249, None),
    ("SKU-2003", "Power Bank 10000mAh", "electronics", 500, 799, None),
    ("SKU-2004", "Bluetooth Earphones", "electronics", 350, 599, None),
    ("SKU-2005", "Wireless Mouse", "electronics", 200, 349, None),  # dedicated slow-mover clearance demo
]
products = {}
for sku, name, category, cost, price, expiry_offset in product_defs:
    expiry = (date.today() + timedelta(days=expiry_offset)) if expiry_offset is not None else None
    p = Product(
        sku=sku,
        name=name,
        category=category,
        cost=Decimal(cost),
        price=Decimal(price),
        realm_id=realm.id,
        expiry_date=expiry,
    )
    db.add(p)
    db.flush()
    products[sku] = p

db.commit()

retail_stores = ["Chennai Central", "Ambattur Hub", "Coimbatore Store", "Madurai Store"]

# --- scenario matrix: (sku, store) -> (avg_daily_demand, inventory) ---
# avg_daily_demand == 0 means "never sold" for that store, which (combined
# across all stores) drives days_since_last_sold to 999 for that product.
# This is what makes the DONATE / bundle / slow-mover demos deterministic.
scenarios = {
    # Rice: Chennai Central stockout, Ambattur healthy, Coimbatore overstock -> TRANSFER candidate
    ("SKU-1001", "Chennai Central"): (12, 20),
    ("SKU-1001", "Ambattur Hub"): (8, 160),
    ("SKU-1001", "Coimbatore Store"): (3, 400),
    ("SKU-1001", "Madurai Store"): (6, 110),

    # Sugar: mostly healthy
    ("SKU-1002", "Chennai Central"): (10, 180),
    ("SKU-1002", "Ambattur Hub"): (9, 160),
    ("SKU-1002", "Coimbatore Store"): (7, 130),
    ("SKU-1002", "Madurai Store"): (6, 20),  # near-stockout

    # Milk: fast mover at retail (irrelevant to the DISCARD demo, which is
    # driven entirely by the warehouse's expired batch)
    ("SKU-1003", "Chennai Central"): (25, 60),
    ("SKU-1003", "Ambattur Hub"): (18, 15),  # stockout risk
    ("SKU-1003", "Coimbatore Store"): (15, 45),
    ("SKU-1003", "Madurai Store"): (12, 40),

    # Tea powder: zero retail sales anywhere -> global "never sold" -> DONATE (food)
    ("SKU-1004", "Chennai Central"): (0, 300),
    ("SKU-1004", "Ambattur Hub"): (0, 220),
    ("SKU-1004", "Coimbatore Store"): (0, 260),
    ("SKU-1004", "Madurai Store"): (0, 180),

    # Cooking oil: healthy
    ("SKU-1005", "Chennai Central"): (8, 140),
    ("SKU-1005", "Ambattur Hub"): (6, 100),
    ("SKU-1005", "Coimbatore Store"): (5, 90),
    ("SKU-1005", "Madurai Store"): (4, 70),

    # Biscuits: healthy/recent sales at retail; the warehouse batch is
    # separately expiring soon -> CLEARANCE (expiry tier), regardless
    ("SKU-1006", "Chennai Central"): (20, 250),
    ("SKU-1006", "Ambattur Hub"): (10, 150),
    ("SKU-1006", "Coimbatore Store"): (9, 140),
    ("SKU-1006", "Madurai Store"): (8, 120),

    # LED Bulb: zero sales anywhere -> global "never sold" -> DONATE (non-food)
    ("SKU-2001", "Chennai Central"): (0, 15),
    ("SKU-2001", "Ambattur Hub"): (0, 10),
    ("SKU-2001", "Coimbatore Store"): (0, 0),
    ("SKU-2001", "Madurai Store"): (0, 0),

    # Mobile Charger: stockout at one store, overstock at another -> TRANSFER candidate
    ("SKU-2002", "Chennai Central"): (4, 3),   # stockout risk
    ("SKU-2002", "Ambattur Hub"): (2, 90),      # overstock -> transfer source
    ("SKU-2002", "Coimbatore Store"): (2, 25),
    ("SKU-2002", "Madurai Store"): (1, 20),

    # Power Bank: healthy, higher value item
    ("SKU-2003", "Chennai Central"): (3, 35),
    ("SKU-2003", "Ambattur Hub"): (2, 20),
    ("SKU-2003", "Coimbatore Store"): (2, 22),
    ("SKU-2003", "Madurai Store"): (1, 15),

    # Bluetooth Earphones: zero retail sales -> global "never sold";
    # warehouse qty deliberately kept in the 15-49 band -> CLEARANCE (bundle)
    ("SKU-2004", "Chennai Central"): (0, 130),
    ("SKU-2004", "Ambattur Hub"): (0, 110),
    ("SKU-2004", "Coimbatore Store"): (0, 95),
    ("SKU-2004", "Madurai Store"): (0, 60),

    # Wireless Mouse: no retail footprint at all. Its only sale is the
    # single historical row added below, dated 35 days ago.
}

# Warehouse-held stock. Only products with a row here are considered by
# SmartInventoryActionEngine at all, since it pulls from the warehouse's
# InventoryStock. Each quantity/threshold below is picked deliberately:
warehouse_stock = {
    "SKU-1003": 40,    # Milk Packet   -> DISCARD (food + expired, qty doesn't matter)
    "SKU-1004": 150,   # Tea Powder    -> DONATE, food (>=50 qty, never sold, expiry 90d out)
    "SKU-2001": 400,   # LED Bulb      -> DONATE, non-food (>=50 qty, never sold, no expiry)
    "SKU-2004": 30,    # Earphones     -> CLEARANCE bundle (15-49 qty band, non-food, never sold)
    "SKU-1006": 20,    # Biscuits      -> CLEARANCE expiry tier (food, expires in 10 days, <=14d tier = 40%)
    "SKU-2005": 8,     # Wireless Mouse-> CLEARANCE slow-mover tier only (qty <15 so bundle can't fire)
}

# --- write inventory_stock (retail) ---
for (sku, store_name), (_, inv) in scenarios.items():
    db.add(InventoryStock(
        product_id=products[sku].id,
        store_id=stores[store_name].id,
        quantity=inv,
        last_updated=date.today(),
        realm_id=realm.id,
    ))

# --- write inventory_stock (warehouse) ---
for sku, qty in warehouse_stock.items():
    db.add(InventoryStock(
        product_id=products[sku].id,
        store_id=stores["Warehouse"].id,
        quantity=qty,
        last_updated=date.today(),
        realm_id=realm.id,
    ))

db.commit()

# --- write 60 days of sales so demand + demand_growth are both derivable ---
today = date.today()
for (sku, store_name), (avg_daily, _) in scenarios.items():
    if avg_daily <= 0:
        continue
    product = products[sku]
    store = stores[store_name]
    for offset in range(60):
        d = today - timedelta(days=offset)
        # small day-to-day noise, and a mild growth trend in the last 30 days for a couple of SKUs
        noise = random.uniform(0.7, 1.3)
        trend = 1.15 if (offset < 30 and sku in ("SKU-1003", "SKU-1006")) else 1.0
        qty = max(0, round(avg_daily * noise * trend))
        if qty == 0:
            continue
        db.add(Sale(
            product_id=product.id,
            store_id=store.id,
            sale_date=d,
            quantity=qty,
            revenue=Decimal(qty) * product.price,
            realm_id=realm.id,
        ))

# --- one deliberate historical sale for Wireless Mouse, dated 35 days ago ---
# This is what makes days_since_last_sold land at exactly 35, which sits in
# the slow-mover tier band [30, 45) -> 20% clearance discount, without ever
# touching the bundle rule (that needs warehouse qty >= 15; Mouse is 8).
db.add(Sale(
    product_id=products["SKU-2005"].id,
    store_id=stores["Chennai Central"].id,
    sale_date=today - timedelta(days=35),
    quantity=2,
    revenue=Decimal(2) * products["SKU-2005"].price,
    realm_id=realm.id,
))

db.commit()
print("Seed complete.")