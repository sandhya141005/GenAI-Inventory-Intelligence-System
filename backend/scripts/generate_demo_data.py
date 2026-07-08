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
# Near the top of your script, add 'text' to your sqlalchemy imports if not present
from sqlalchemy import text

# ... (connection setup code) ...

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

# --- REST OF YOUR SEED CODE CONTINUES BELOW ---
random.seed(42)
db = SessionLocal()
db.query(Sale).delete()
db.query(Transfer).delete()
db.query(InventoryStock).delete()
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

# --- products: groceries + electronics only ---
product_defs = [
    # sku, name, category, cost, price
    ("SKU-1001", "Rice 5kg", "groceries", 180, 240),
    ("SKU-1002", "Sugar 1kg", "groceries", 38, 52),
    ("SKU-1003", "Milk Packet", "groceries", 22, 30),
    ("SKU-1004", "Tea Powder 250g", "groceries", 90, 130),
    ("SKU-1005", "Cooking Oil 1L", "groceries", 110, 150),
    ("SKU-1006", "Biscuits Pack", "groceries", 18, 25),
    ("SKU-2001", "LED Bulb 9W", "electronics", 60, 99),
    ("SKU-2002", "Mobile Charger", "electronics", 150, 249),
    ("SKU-2003", "Power Bank 10000mAh", "electronics", 500, 799),
    ("SKU-2004", "Bluetooth Earphones", "electronics", 350, 599),
]
products = {}
for sku, name, category, cost, price in product_defs:
    # Inject an absolute past expiry date onto a perishable item to fire DISCARD
    expiry = date.today() - timedelta(days=2) if sku == "SKU-1003" else None
    
    p = Product(
        sku=sku, 
        name=name, 
        category=category, 
        cost=Decimal(cost), 
        price=Decimal(price), 
        realm_id=realm.id,
        expiry_date=expiry
    )
    db.add(p)
    db.flush()
    products[sku] = p

db.commit()

retail_stores = ["Chennai Central", "Ambattur Hub", "Coimbatore Store", "Madurai Store"]

# --- scenario matrix: (sku, store) -> (avg_daily_demand, inventory) ---
# built to cover: stockout, healthy, overstock, transfer opportunity
scenarios = {
    # Rice: Chennai Central stockout, Ambattur healthy, Coimbatore overstock -> transfer candidate
    ("SKU-1001", "Chennai Central"): (12, 20),
    ("SKU-1001", "Ambattur Hub"): (8, 160),
    ("SKU-1001", "Coimbatore Store"): (3, 400),
    ("SKU-1001", "Madurai Store"): (6, 110),

    # Sugar: mostly healthy
    ("SKU-1002", "Chennai Central"): (10, 180),
    ("SKU-1002", "Ambattur Hub"): (9, 160),
    ("SKU-1002", "Coimbatore Store"): (7, 130),
    ("SKU-1002", "Madurai Store"): (6, 20),  # near-stockout

    # Milk: fast mover, tight coverage everywhere
    ("SKU-1003", "Chennai Central"): (25, 60),
    ("SKU-1003", "Ambattur Hub"): (18, 15),  # stockout risk
    ("SKU-1003", "Coimbatore Store"): (15, 45),
    ("SKU-1003", "Madurai Store"): (12, 40),

    # Tea powder: overstock across the board, dead stock
    ("SKU-1004", "Chennai Central"): (0, 300),
    ("SKU-1004", "Ambattur Hub"): (0, 220),
    ("SKU-1004", "Coimbatore Store"): (0, 260),
    ("SKU-1004", "Madurai Store"): (0, 180),
    
    # Cooking oil: healthy
    ("SKU-1005", "Chennai Central"): (8, 140),
    ("SKU-1005", "Ambattur Hub"): (6, 100),
    ("SKU-1005", "Coimbatore Store"): (5, 90),
    ("SKU-1005", "Madurai Store"): (4, 70),

    # Biscuits: healthy, minor demand spike at Chennai Central
    ("SKU-1006", "Chennai Central"): (20, 250),
    ("SKU-1006", "Ambattur Hub"): (10, 150),
    ("SKU-1006", "Coimbatore Store"): (9, 140),
    ("SKU-1006", "Madurai Store"): (8, 120),

    # LED Bulb: low demand, warehouse overstock only, no retail stock
    ("SKU-2001", "Chennai Central"): (0, 15),
    ("SKU-2001", "Ambattur Hub"): (0, 10),
    ("SKU-2001", "Coimbatore Store"): (0, 0),
    ("SKU-2001", "Madurai Store"): (0, 0),

    # Mobile Charger: stockout at one store, overstock at another
    ("SKU-2002", "Chennai Central"): (4, 3),   # stockout risk
    ("SKU-2002", "Ambattur Hub"): (2, 90),      # overstock -> transfer source
    ("SKU-2002", "Coimbatore Store"): (2, 25),
    ("SKU-2002", "Madurai Store"): (1, 20),

    # Power Bank: healthy, higher value item
    ("SKU-2003", "Chennai Central"): (3, 35),
    ("SKU-2003", "Ambattur Hub"): (2, 20),
    ("SKU-2003", "Coimbatore Store"): (2, 22),
    ("SKU-2003", "Madurai Store"): (1, 15),

    # Bluetooth Earphones: aging overstock, dead stock
    ("SKU-2004", "Chennai Central"): (0, 130),
    ("SKU-2004", "Ambattur Hub"): (0, 110),
    ("SKU-2004", "Coimbatore Store"): (0, 95),
    ("SKU-2004", "Madurai Store"): (0, 60),
}

# warehouse holds slow movers with genuinely no retail sales
warehouse_stock = {
    "SKU-2001": 400,   # LED bulbs, dead stock -> qualifies for donation floor (>100 units)
    "SKU-1004": 150,   # tea powder overflow -> breaks down into 15-49 unit bundle band per store
    "SKU-2004": 80,    # Bluetooth earphones -> breaks down into 15-49 unit bundle band per store
}

# --- write inventory_stock ---
for (sku, store_name), (_, inv) in scenarios.items():
    db.add(InventoryStock(
        product_id=products[sku].id,
        store_id=stores[store_name].id,
        quantity=inv,
        last_updated=date.today(),
        realm_id=realm.id,
    ))

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

db.commit()
print("Seed complete.")