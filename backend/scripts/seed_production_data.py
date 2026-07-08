"""
Production Database Seed - Coherent Business Narrative
Represents a realistic retail chain with operational challenges and AI-driven solutions
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import date, timedelta
from decimal import Decimal
from typing import List, Dict, Tuple

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.analytics_data import Product, Store, WarehouseStock, Sale, Transfer, DonationLog
from app.models.user import Realm, STORE_MANAGER, WAREHOUSE_OWNER, User
from app.core.security import hash_password
from app.services.action_engine import SmartInventoryActionEngine
from app.services.analytics_service import AnalyticsService


WAREHOUSES = [
    ("Chennai Flagship", "Chennai", "South", "hub"),
    ("Bangalore Metro", "Bangalore", "South", "store"),
    ("Hyderabad Central", "Hyderabad", "South", "store"),
    ("Coimbatore Regional", "Coimbatore", "South", "store"),
    ("Kochi Fresh Market", "Kochi", "South", "store"),
]

RETAIL_PRODUCTS = [
    ("FOOD-RICE-BR5", "Basmati Rice 5kg Premium", "Food", Decimal("485"), Decimal("340"), 180),
    ("FOOD-RICE-WH1", "White Rice 1kg", "Food", Decimal("65"), Decimal("42"), 180),
    ("FOOD-OIL-SUN", "Sunflower Oil 1L", "Food", Decimal("165"), Decimal("120"), 90),
    ("FOOD-OIL-OLV", "Olive Oil 500ml Premium", "Food", Decimal("520"), Decimal("380"), 60),
    ("FOOD-DAL-TR", "Toor Dal 1kg", "Food", Decimal("145"), Decimal("105"), 365),
    ("FOOD-FLOUR-WH", "Wheat Flour 5kg", "Food", Decimal("240"), Decimal("175"), 120),
    ("FOOD-SUGAR-WH", "White Sugar 1kg", "Food", Decimal("48"), Decimal("34"), 730),
    ("FOOD-SALT-IO", "Iodized Salt 1kg", "Food", Decimal("22"), Decimal("15"), 1095),
    
    ("BEV-JUICE-ORA", "Fresh Orange Juice 1L", "Beverages", Decimal("95"), Decimal("62"), 7),
    ("BEV-JUICE-MAN", "Mango Nectar 1L", "Beverages", Decimal("105"), Decimal("68"), 14),
    ("BEV-WATER-MIN", "Mineral Water 20L Can", "Beverages", Decimal("75"), Decimal("45"), 180),
    ("BEV-COLA-2L", "Premium Cola 2L", "Beverages", Decimal("85"), Decimal("52"), 90),
    ("BEV-TEA-GRN", "Green Tea Organic 100g", "Beverages", Decimal("220"), Decimal("145"), 730),
    ("BEV-COFFEE-INS", "Instant Coffee Premium 100g", "Beverages", Decimal("285"), Decimal("195"), 730),
    ("BEV-MILK-TET", "Tetra Pack Milk 1L", "Beverages", Decimal("62"), Decimal("42"), 5),
    
    ("SNACK-CHIP-POT", "Potato Chips Classic 200g", "Snacks", Decimal("45"), Decimal("28"), 60),
    ("SNACK-CHIP-COR", "Corn Chips Spicy 150g", "Snacks", Decimal("38"), Decimal("24"), 45),
    ("SNACK-BISC-CRM", "Cream Biscuits Family 300g", "Snacks", Decimal("52"), Decimal("33"), 90),
    ("SNACK-NUTS-CSH", "Premium Cashews 250g", "Snacks", Decimal("420"), Decimal("310"), 365),
    ("SNACK-CHOC-BAR", "Dark Chocolate Bar 50g", "Snacks", Decimal("45"), Decimal("28"), 180),
    ("SNACK-COOKIES", "Butter Cookies 250g", "Snacks", Decimal("68"), Decimal("42"), 90),
    
    ("CARE-SOAP-BAT", "Premium Bathing Soap 125g", "Personal Care", Decimal("42"), Decimal("26"), 1095),
    ("CARE-SHAMP-HER", "Herbal Shampoo 200ml", "Personal Care", Decimal("195"), Decimal("135"), 730),
    ("CARE-TOOTH-PAS", "Toothpaste Whitening 150g", "Personal Care", Decimal("105"), Decimal("68"), 730),
    ("CARE-CREAM-FAC", "Face Cream Daily 50ml", "Personal Care", Decimal("320"), Decimal("215"), 545),
    ("CARE-LOTION-BOD", "Body Lotion 200ml", "Personal Care", Decimal("245"), Decimal("165"), 545),
    ("CARE-DEODR-SPR", "Deodorant Spray 150ml", "Personal Care", Decimal("165"), Decimal("110"), 730),
    
    ("CLEAN-DET-POW", "Detergent Powder 1kg", "Cleaning", Decimal("185"), Decimal("125"), None),
    ("CLEAN-SOAP-DSH", "Dish Wash Gel 500ml", "Cleaning", Decimal("95"), Decimal("62"), None),
    ("CLEAN-FLOOR-LIQ", "Floor Cleaner 1L", "Cleaning", Decimal("145"), Decimal("95"), None),
    ("CLEAN-TOIL-CLN", "Toilet Cleaner 500ml", "Cleaning", Decimal("85"), Decimal("55"), None),
    ("CLEAN-GLASS-SPR", "Glass Cleaner Spray 500ml", "Cleaning", Decimal("125"), Decimal("80"), None),
    
    ("STAT-PEN-BALL", "Ball Point Pens Blue 10pc", "Stationery", Decimal("85"), Decimal("52"), None),
    ("STAT-NOTE-A4", "Ruled Notebook A4 200pg", "Stationery", Decimal("105"), Decimal("68"), None),
    ("STAT-PENCIL-HB", "HB Pencils Box 12pc", "Stationery", Decimal("72"), Decimal("45"), None),
    ("STAT-MARKER-SET", "Permanent Markers 6 Colors", "Stationery", Decimal("155"), Decimal("95"), None),
    
    ("HOME-BULB-LED9", "LED Bulb 9W Cool White", "Household", Decimal("135"), Decimal("82"), None),
    ("HOME-BULB-L12", "LED Bulb 12W Warm White", "Household", Decimal("175"), Decimal("115"), None),
    ("HOME-CORD-EXT", "Extension Cord 5m 3-Socket", "Household", Decimal("320"), Decimal("205"), None),
    ("HOME-BATT-AA", "AA Alkaline Batteries 4pc", "Household", Decimal("105"), Decimal("65"), None),
    ("HOME-TORCH-LED", "LED Torch Rechargeable", "Household", Decimal("385"), Decimal("245"), None),
    
    ("MED-PARA-TAB", "Paracetamol 500mg 10 Tabs", "Medicine", Decimal("28"), Decimal("18"), 18),
    ("MED-VITA-MULT", "Multivitamin Tablets 30pc", "Medicine", Decimal("320"), Decimal("215"), 24),
    ("MED-COUGH-SYR", "Cough Syrup 100ml", "Medicine", Decimal("105"), Decimal("68"), 36),
    ("MED-BALM-PAIN", "Pain Relief Balm 25g", "Medicine", Decimal("95"), Decimal("62"), 730),
    ("MED-BANDAGE", "Adhesive Bandages 20pc", "Medicine", Decimal("65"), Decimal("42"), 1095),
    
    ("BABY-DIAP-MED", "Baby Diapers Medium 40pc", "Baby Products", Decimal("685"), Decimal("475"), None),
    ("BABY-DIAP-LRG", "Baby Diapers Large 36pc", "Baby Products", Decimal("725"), Decimal("505"), None),
    ("BABY-POWD-TAL", "Baby Talcum Powder 200g", "Baby Products", Decimal("155"), Decimal("105"), 730),
    ("BABY-SOAP-MIL", "Baby Soap Mild 75g", "Baby Products", Decimal("72"), Decimal("48"), 1095),
    ("BABY-OIL-MASS", "Baby Massage Oil 200ml", "Baby Products", Decimal("195"), Decimal("135"), 545),
    ("BABY-WIPES", "Baby Wet Wipes 80pc", "Baby Products", Decimal("145"), Decimal("95"), 365),
    
    ("ELEC-CABLE-USB", "USB-C Cable 2m", "Electronics Accessories", Decimal("195"), Decimal("125"), None),
    ("ELEC-CHRG-FAST", "Fast Charger 18W", "Electronics Accessories", Decimal("385"), Decimal("245"), None),
    ("ELEC-EARPH-WIR", "Wired Earphones Premium", "Electronics Accessories", Decimal("320"), Decimal("205"), None),
    ("ELEC-HOLD-CAR", "Car Phone Holder", "Electronics Accessories", Decimal("175"), Decimal("110"), None),
]


BUSINESS_NARRATIVE = """
STOCKLENS RETAIL CHAIN - OPERATIONAL SITUATION

Timeline (Last 6 Months):
- January-February: Normal operations, steady growth
- March: Regional supplier disruption affects Bangalore supply chain
- April: Bangalore experiences stockouts, emergency transfers from Chennai
- May: Hyderabad over-ordered to prevent shortages, creating overstock
- June: Inventory aging issues emerge in Hyderabad and Coimbatore
- July (Current): Multiple action opportunities across network

Current Warehouse States:

CHENNAI FLAGSHIP (Healthy Hub)
- Strong revenue performance
- Balanced inventory levels
- Served as emergency transfer source in April
- Highest customer satisfaction
- Some products sent to Bangalore during crisis

BANGALORE METRO (High Demand, Stockouts)
- Supplier disruption in March-April
- Multiple ongoing stockouts
- Significant revenue at risk (INR 50,000+)
- Received emergency transfers but still short
- Highest demand in network
- Urgent replenishment needed

HYDERABAD CENTRAL (Overstock Crisis)
- Over-ordered in May to avoid Bangalore situation
- Severe overstock on multiple categories
- Slow inventory turnover
- High carrying costs
- Many products aging without sales
- Transfer opportunities to other warehouses

COIMBATORE REGIONAL (Moderate Aging)
- Stable but declining operations
- Growing inventory age
- Moderate overstock
- Potential transfer source
- Needs promotion activity

KOCHI FRESH MARKET (Expiry Challenges)
- Food-heavy distribution
- Several products nearing expiry
- Donation opportunities (orphanages nearby)
- Clearance sales needed
- Some items already expired (discard required)
"""


def create_realm_and_owner(db: Session) -> Tuple[int, int]:
    email = "ops@stocklens.com"
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        user = User(
            email=email,
            full_name="Operations Director",
            hashed_password=hash_password("stocklens2024"),
            is_active=True,
            role=WAREHOUSE_OWNER,
        )
        db.add(user)
        db.flush()
    
    realm = db.query(Realm).filter(Realm.join_code == "SL24").first()
    if not realm:
        realm = Realm(
            name="StockLens Retail Network",
            industry_tag="Retail Distribution",
            join_code="SL24",
            owner_user_id=user.id,
        )
        db.add(realm)
        db.flush()
    
    user.realm_id = realm.id
    user.role = WAREHOUSE_OWNER
    db.commit()
    db.refresh(user)
    
    return user.id, realm.id


def create_store_managers(db: Session, realm_id: int, stores: List[Store]) -> None:
    managers = [
        ("bangalore.ops@stocklens.com", "Bangalore Operations Manager", stores[1].id),
        ("hyderabad.ops@stocklens.com", "Hyderabad Inventory Manager", stores[2].id),
    ]
    
    for email, name, store_id in managers:
        manager = db.query(User).filter(User.email == email).first()
        if not manager:
            manager = User(
                email=email,
                full_name=name,
                hashed_password=hash_password("stocklens2024"),
                is_active=True,
            )
            db.add(manager)
        manager.realm_id = realm_id
        manager.role = STORE_MANAGER
        manager.assigned_store_id = store_id
    
    db.commit()


class ProductProfile:
    def __init__(self, sku: str, category: str, base_demand: int, narrative_role: str):
        self.sku = sku
        self.category = category
        self.base_demand = base_demand
        self.narrative_role = narrative_role


PRODUCT_NARRATIVES = {
    "FOOD-RICE-BR5": ProductProfile("FOOD-RICE-BR5", "Food", 40, "high_seller"),
    "FOOD-RICE-WH1": ProductProfile("FOOD-RICE-WH1", "Food", 65, "high_seller"),
    "FOOD-OIL-SUN": ProductProfile("FOOD-OIL-SUN", "Food", 50, "bangalore_stockout"),
    "FOOD-OIL-OLV": ProductProfile("FOOD-OIL-OLV", "Food", 12, "premium_slow"),
    "FOOD-DAL-TR": ProductProfile("FOOD-DAL-TR", "Food", 35, "consistent"),
    "FOOD-FLOUR-WH": ProductProfile("FOOD-FLOUR-WH", "Food", 42, "bangalore_stockout"),
    "FOOD-SUGAR-WH": ProductProfile("FOOD-SUGAR-WH", "Food", 55, "high_seller"),
    "FOOD-SALT-IO": ProductProfile("FOOD-SALT-IO", "Food", 48, "consistent"),
    
    "BEV-JUICE-ORA": ProductProfile("BEV-JUICE-ORA", "Beverages", 28, "kochi_expiring"),
    "BEV-JUICE-MAN": ProductProfile("BEV-JUICE-MAN", "Beverages", 25, "kochi_expiring"),
    "BEV-WATER-MIN": ProductProfile("BEV-WATER-MIN", "Beverages", 70, "high_seller"),
    "BEV-COLA-2L": ProductProfile("BEV-COLA-2L", "Beverages", 45, "seasonal_summer"),
    "BEV-TEA-GRN": ProductProfile("BEV-TEA-GRN", "Beverages", 18, "consistent"),
    "BEV-COFFEE-INS": ProductProfile("BEV-COFFEE-INS", "Beverages", 22, "consistent"),
    "BEV-MILK-TET": ProductProfile("BEV-MILK-TET", "Beverages", 85, "kochi_expired"),
    
    "SNACK-CHIP-POT": ProductProfile("SNACK-CHIP-POT", "Snacks", 75, "high_seller"),
    "SNACK-CHIP-COR": ProductProfile("SNACK-CHIP-COR", "Snacks", 60, "kochi_expiring"),
    "SNACK-BISC-CRM": ProductProfile("SNACK-BISC-CRM", "Snacks", 52, "consistent"),
    "SNACK-NUTS-CSH": ProductProfile("SNACK-NUTS-CSH", "Snacks", 15, "premium_slow"),
    "SNACK-CHOC-BAR": ProductProfile("SNACK-CHOC-BAR", "Snacks", 38, "consistent"),
    "SNACK-COOKIES": ProductProfile("SNACK-COOKIES", "Snacks", 28, "hyderabad_overstock"),
    
    "CARE-SOAP-BAT": ProductProfile("CARE-SOAP-BAT", "Personal Care", 95, "bangalore_stockout"),
    "CARE-SHAMP-HER": ProductProfile("CARE-SHAMP-HER", "Personal Care", 30, "consistent"),
    "CARE-TOOTH-PAS": ProductProfile("CARE-TOOTH-PAS", "Personal Care", 48, "consistent"),
    "CARE-CREAM-FAC": ProductProfile("CARE-CREAM-FAC", "Personal Care", 12, "hyderabad_overstock"),
    "CARE-LOTION-BOD": ProductProfile("CARE-LOTION-BOD", "Personal Care", 18, "hyderabad_overstock"),
    "CARE-DEODR-SPR": ProductProfile("CARE-DEODR-SPR", "Personal Care", 35, "seasonal_summer"),
    
    "CLEAN-DET-POW": ProductProfile("CLEAN-DET-POW", "Cleaning", 45, "consistent"),
    "CLEAN-SOAP-DSH": ProductProfile("CLEAN-SOAP-DSH", "Cleaning", 52, "consistent"),
    "CLEAN-FLOOR-LIQ": ProductProfile("CLEAN-FLOOR-LIQ", "Cleaning", 38, "consistent"),
    "CLEAN-TOIL-CLN": ProductProfile("CLEAN-TOIL-CLN", "Cleaning", 42, "consistent"),
    "CLEAN-GLASS-SPR": ProductProfile("CLEAN-GLASS-SPR", "Cleaning", 25, "slow_mover"),
    
    "STAT-PEN-BALL": ProductProfile("STAT-PEN-BALL", "Stationery", 30, "consistent"),
    "STAT-NOTE-A4": ProductProfile("STAT-NOTE-A4", "Stationery", 25, "seasonal_schools"),
    "STAT-PENCIL-HB": ProductProfile("STAT-PENCIL-HB", "Stationery", 20, "seasonal_schools"),
    "STAT-MARKER-SET": ProductProfile("STAT-MARKER-SET", "Stationery", 12, "slow_mover"),
    
    "HOME-BULB-LED9": ProductProfile("HOME-BULB-LED9", "Household", 40, "consistent"),
    "HOME-BULB-L12": ProductProfile("HOME-BULB-L12", "Household", 28, "consistent"),
    "HOME-CORD-EXT": ProductProfile("HOME-CORD-EXT", "Household", 15, "coimbatore_aging"),
    "HOME-BATT-AA": ProductProfile("HOME-BATT-AA", "Household", 32, "consistent"),
    "HOME-TORCH-LED": ProductProfile("HOME-TORCH-LED", "Household", 18, "slow_mover"),
    
    "MED-PARA-TAB": ProductProfile("MED-PARA-TAB", "Medicine", 120, "kochi_expiring"),
    "MED-VITA-MULT": ProductProfile("MED-VITA-MULT", "Medicine", 22, "kochi_expired"),
    "MED-COUGH-SYR": ProductProfile("MED-COUGH-SYR", "Medicine", 35, "seasonal_winter"),
    "MED-BALM-PAIN": ProductProfile("MED-BALM-PAIN", "Medicine", 28, "consistent"),
    "MED-BANDAGE": ProductProfile("MED-BANDAGE", "Medicine", 45, "consistent"),
    
    "BABY-DIAP-MED": ProductProfile("BABY-DIAP-MED", "Baby Products", 85, "high_seller"),
    "BABY-DIAP-LRG": ProductProfile("BABY-DIAP-LRG", "Baby Products", 75, "high_seller"),
    "BABY-POWD-TAL": ProductProfile("BABY-POWD-TAL", "Baby Products", 32, "hyderabad_overstock"),
    "BABY-SOAP-MIL": ProductProfile("BABY-SOAP-MIL", "Baby Products", 40, "consistent"),
    "BABY-OIL-MASS": ProductProfile("BABY-OIL-MASS", "Baby Products", 28, "hyderabad_overstock"),
    "BABY-WIPES": ProductProfile("BABY-WIPES", "Baby Products", 65, "high_seller"),
    
    "ELEC-CABLE-USB": ProductProfile("ELEC-CABLE-USB", "Electronics Accessories", 25, "consistent"),
    "ELEC-CHRG-FAST": ProductProfile("ELEC-CHRG-FAST", "Electronics Accessories", 18, "slow_mover"),
    "ELEC-EARPH-WIR": ProductProfile("ELEC-EARPH-WIR", "Electronics Accessories", 22, "consistent"),
    "ELEC-HOLD-CAR": ProductProfile("ELEC-HOLD-CAR", "Electronics Accessories", 12, "coimbatore_aging"),
}


def generate_sales_history(db: Session, products: List[Product], stores: List[Store], realm_id: int, today: date) -> int:
    chennai, bangalore, hyderabad, coimbatore, kochi = stores
    sales_count = 0
    start_date = today - timedelta(days=180)
    
    product_map = {p.sku: p for p in products}
    
    for day_offset in range(180):
        current_date = start_date + timedelta(days=day_offset)
        days_ago = 180 - day_offset
        month = current_date.month
        is_weekend = current_date.weekday() >= 5
        
        month_phase = "normal"
        if month in [1, 2]:
            month_phase = "normal"
        elif month == 3:
            month_phase = "disruption_start"
        elif month == 4:
            month_phase = "disruption_peak"
        elif month == 5:
            month_phase = "recovery"
        elif month in [6, 7]:
            month_phase = "stabilization"
        
        for sku, profile in PRODUCT_NARRATIVES.items():
            product = product_map.get(sku)
            if not product:
                continue
            
            base = profile.base_demand
            role = profile.narrative_role
            
            if role == "high_seller":
                demand_factor = 1.2
                if is_weekend:
                    demand_factor *= 1.3
                for store in stores:
                    qty = max(0, int(base * demand_factor * (0.9 + (day_offset / 900))))
                    if qty > 0:
                        sale = Sale(
                            realm_id=realm_id,
                            product_id=product.id,
                            store_id=store.id,
                            quantity=qty,
                            revenue=product.price * Decimal(qty),
                            sale_date=current_date,
                        )
                        db.add(sale)
                        sales_count += 1
            
            elif role == "bangalore_stockout":
                if month_phase in ["normal"]:
                    demand_factor = 1.0
                    for store in [chennai, bangalore, hyderabad]:
                        qty = int(base * demand_factor)
                        if qty > 0:
                            sale = Sale(
                                realm_id=realm_id,
                                product_id=product.id,
                                store_id=store.id,
                                quantity=qty,
                                revenue=product.price * Decimal(qty),
                                sale_date=current_date,
                            )
                            db.add(sale)
                            sales_count += 1
                
                elif month_phase == "disruption_start":
                    for store in [chennai, hyderabad]:
                        qty = int(base * 1.0)
                        sale = Sale(
                            realm_id=realm_id,
                            product_id=product.id,
                            store_id=store.id,
                            quantity=qty,
                            revenue=product.price * Decimal(qty),
                            sale_date=current_date,
                        )
                        db.add(sale)
                        sales_count += 1
                    
                    if current_date.day > 15:
                        qty = int(base * 0.3)
                        if qty > 0:
                            sale = Sale(
                                realm_id=realm_id,
                                product_id=product.id,
                                store_id=bangalore.id,
                                quantity=qty,
                                revenue=product.price * Decimal(qty),
                                sale_date=current_date,
                            )
                            db.add(sale)
                            sales_count += 1
                
                elif month_phase == "disruption_peak":
                    for store in [chennai, hyderabad]:
                        qty = int(base * 1.0)
                        sale = Sale(
                            realm_id=realm_id,
                            product_id=product.id,
                            store_id=store.id,
                            quantity=qty,
                            revenue=product.price * Decimal(qty),
                            sale_date=current_date,
                        )
                        db.add(sale)
                        sales_count += 1
                
                elif month_phase in ["recovery", "stabilization"]:
                    demand_factor = 0.7 if month_phase == "recovery" else 0.85
                    for store in stores:
                        qty = int(base * demand_factor)
                        if qty > 0:
                            sale = Sale(
                                realm_id=realm_id,
                                product_id=product.id,
                                store_id=store.id,
                                quantity=qty,
                                revenue=product.price * Decimal(qty),
                                sale_date=current_date,
                            )
                            db.add(sale)
                            sales_count += 1
            
            elif role == "hyderabad_overstock":
                if month_phase in ["normal", "disruption_start", "disruption_peak"]:
                    for store in [chennai, bangalore, coimbatore]:
                        qty = int(base * 0.8)
                        sale = Sale(
                            realm_id=realm_id,
                            product_id=product.id,
                            store_id=store.id,
                            quantity=qty,
                            revenue=product.price * Decimal(qty),
                            sale_date=current_date,
                        )
                        db.add(sale)
                        sales_count += 1
                    
                    qty = int(base * 1.2)
                    sale = Sale(
                        realm_id=realm_id,
                        product_id=product.id,
                        store_id=hyderabad.id,
                        quantity=qty,
                        revenue=product.price * Decimal(qty),
                        sale_date=current_date,
                    )
                    db.add(sale)
                    sales_count += 1
                
                else:
                    for store in [chennai, bangalore]:
                        qty = int(base * 0.7)
                        sale = Sale(
                            realm_id=realm_id,
                            product_id=product.id,
                            store_id=store.id,
                            quantity=qty,
                            revenue=product.price * Decimal(qty),
                            sale_date=current_date,
                        )
                        db.add(sale)
                        sales_count += 1
                    
                    if current_date.day % 3 == 0:
                        qty = int(base * 0.3)
                        sale = Sale(
                            realm_id=realm_id,
                            product_id=product.id,
                            store_id=hyderabad.id,
                            quantity=qty,
                            revenue=product.price * Decimal(qty),
                            sale_date=current_date,
                        )
                        db.add(sale)
                        sales_count += 1
            
            elif role == "kochi_expiring" or role == "kochi_expired":
                if days_ago > 90:
                    qty = int(base * 1.0)
                    sale = Sale(
                        realm_id=realm_id,
                        product_id=product.id,
                        store_id=kochi.id,
                        quantity=qty,
                        revenue=product.price * Decimal(qty),
                        sale_date=current_date,
                    )
                    db.add(sale)
                    sales_count += 1
                elif days_ago > 45:
                    if current_date.day % 2 == 0:
                        qty = int(base * 0.4)
                        sale = Sale(
                            realm_id=realm_id,
                            product_id=product.id,
                            store_id=kochi.id,
                            quantity=qty,
                            revenue=product.price * Decimal(qty),
                            sale_date=current_date,
                        )
                        db.add(sale)
                        sales_count += 1
            
            elif role == "coimbatore_aging":
                if days_ago > 120:
                    qty = int(base * 0.8)
                    sale = Sale(
                        realm_id=realm_id,
                        product_id=product.id,
                        store_id=coimbatore.id,
                        quantity=qty,
                        revenue=product.price * Decimal(qty),
                        sale_date=current_date,
                    )
                    db.add(sale)
                    sales_count += 1
                elif days_ago > 60:
                    if current_date.day % 3 == 0:
                        qty = int(base * 0.3)
                        sale = Sale(
                            realm_id=realm_id,
                            product_id=product.id,
                            store_id=coimbatore.id,
                            quantity=qty,
                            revenue=product.price * Decimal(qty),
                            sale_date=current_date,
                        )
                        db.add(sale)
                        sales_count += 1
            
            elif role == "consistent":
                for store in stores:
                    qty = int(base * (1.1 if is_weekend else 1.0))
                    if qty > 0:
                        sale = Sale(
                            realm_id=realm_id,
                            product_id=product.id,
                            store_id=store.id,
                            quantity=qty,
                            revenue=product.price * Decimal(qty),
                            sale_date=current_date,
                        )
                        db.add(sale)
                        sales_count += 1
            
            elif role == "seasonal_summer":
                if month in [3, 4, 5, 6]:
                    for store in stores:
                        qty = int(base * 1.5)
                        sale = Sale(
                            realm_id=realm_id,
                            product_id=product.id,
                            store_id=store.id,
                            quantity=qty,
                            revenue=product.price * Decimal(qty),
                            sale_date=current_date,
                        )
                        db.add(sale)
                        sales_count += 1
                else:
                    if current_date.day % 2 == 0:
                        for store in stores:
                            qty = int(base * 0.5)
                            sale = Sale(
                                realm_id=realm_id,
                                product_id=product.id,
                                store_id=store.id,
                                quantity=qty,
                                revenue=product.price * Decimal(qty),
                                sale_date=current_date,
                            )
                            db.add(sale)
                            sales_count += 1
            
            elif role == "seasonal_winter":
                if month in [11, 12, 1, 2]:
                    for store in stores:
                        qty = int(base * 1.4)
                        sale = Sale(
                            realm_id=realm_id,
                            product_id=product.id,
                            store_id=store.id,
                            quantity=qty,
                            revenue=product.price * Decimal(qty),
                            sale_date=current_date,
                        )
                        db.add(sale)
                        sales_count += 1
                else:
                    if current_date.day % 3 == 0:
                        for store in [chennai, bangalore]:
                            qty = int(base * 0.4)
                            sale = Sale(
                                realm_id=realm_id,
                                product_id=product.id,
                                store_id=store.id,
                                quantity=qty,
                                revenue=product.price * Decimal(qty),
                                sale_date=current_date,
                            )
                            db.add(sale)
                            sales_count += 1
            
            elif role == "seasonal_schools":
                if month in [6, 7]:
                    for store in stores:
                        qty = int(base * 2.0)
                        sale = Sale(
                            realm_id=realm_id,
                            product_id=product.id,
                            store_id=store.id,
                            quantity=qty,
                            revenue=product.price * Decimal(qty),
                            sale_date=current_date,
                        )
                        db.add(sale)
                        sales_count += 1
                else:
                    if current_date.day % 4 == 0:
                        for store in [chennai, bangalore]:
                            qty = int(base * 0.4)
                            sale = Sale(
                                realm_id=realm_id,
                                product_id=product.id,
                                store_id=store.id,
                                quantity=qty,
                                revenue=product.price * Decimal(qty),
                                sale_date=current_date,
                            )
                            db.add(sale)
                            sales_count += 1
            
            elif role == "slow_mover" or role == "premium_slow":
                if current_date.day % 5 == 0:
                    for store in [chennai, bangalore]:
                        qty = int(base * 0.3)
                        if qty > 0:
                            sale = Sale(
                                realm_id=realm_id,
                                product_id=product.id,
                                store_id=store.id,
                                quantity=qty,
                                revenue=product.price * Decimal(qty),
                                sale_date=current_date,
                            )
                            db.add(sale)
                            sales_count += 1
    
    return sales_count


def seed_database():
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("🚀 STOCKLENS RETAIL - NARRATIVE-DRIVEN SEED")
        print("="*70)
        
        print("\n🗑️  Clearing existing data...")
        for user in db.query(User).filter(User.assigned_store_id.isnot(None)).all():
            user.assigned_store_id = None
        db.commit()
        
        db.query(DonationLog).delete()
        db.query(Sale).delete()
        db.query(Transfer).delete()
        db.query(WarehouseStock).delete()
        db.query(Product).delete()
        db.query(Store).delete()
        db.commit()
        
        _, realm_id = create_realm_and_owner(db)
        
        print("\n🏪 Creating warehouse network...")
        stores = []
        for name, city, region, store_type in WAREHOUSES:
            store = Store(
                realm_id=realm_id,
                name=name,
                city=city,
                region=region,
                store_type=store_type,
            )
            db.add(store)
            stores.append(store)
        db.commit()
        
        chennai, bangalore, hyderabad, coimbatore, kochi = stores
        print(f"   ✓ Chennai Flagship (Healthy Hub)")
        print(f"   ✓ Bangalore Metro (Stockouts)")
        print(f"   ✓ Hyderabad Central (Overstock)")
        print(f"   ✓ Coimbatore Regional (Aging)")
        print(f"   ✓ Kochi Fresh Market (Expiry)")
        
        create_store_managers(db, realm_id, stores)
        
        today = date.today()
        
        print("\n📦 Creating product catalog...")
        products = []
        for sku, name, category, price, cost, expiry_days in RETAIL_PRODUCTS:
            expiry_date = None
            if expiry_days is not None:
                profile = PRODUCT_NARRATIVES.get(sku)
                if profile and profile.narrative_role == "kochi_expired":
                    expiry_date = today - timedelta(days=2)
                elif profile and profile.narrative_role == "kochi_expiring":
                    expiry_date = today + timedelta(days=4)
                elif profile and profile.narrative_role == "bangalore_stockout":
                    expiry_date = today + timedelta(days=expiry_days)
                else:
                    expiry_date = today + timedelta(days=expiry_days)
            
            product = Product(
                realm_id=realm_id,
                sku=sku,
                name=name,
                category=category,
                price=price,
                cost=cost,
                expiry_date=expiry_date,
            )
            db.add(product)
            products.append(product)
        db.commit()
        print(f"   ✓ {len(products)} products with narrative roles")
        
        print("\n💰 Generating 6-month sales history...")
        sales_count = generate_sales_history(db, products, stores, realm_id, today)
        db.commit()
        print(f"   ✓ {sales_count:,} sales transactions")
        print(f"   ✓ Jan-Feb: Normal operations")
        print(f"   ✓ March: Supplier disruption begins")
        print(f"   ✓ April: Bangalore stockouts peak")
        print(f"   ✓ May: Recovery + Hyderabad over-ordering")
        print(f"   ✓ June-July: Stabilization")
        
        print("\n📊 Setting inventory levels by narrative...")
        product_map = {p.sku: p for p in products}
        
        for sku, profile in PRODUCT_NARRATIVES.items():
            product = product_map.get(sku)
            if not product:
                continue
            
            role = profile.narrative_role
            base = profile.base_demand
            
            if role == "high_seller":
                qty = base * 40
            elif role == "bangalore_stockout":
                qty = base * 2
            elif role == "hyderabad_overstock":
                qty = base * 150
            elif role == "kochi_expiring":
                qty = base * 8
            elif role == "kochi_expired":
                qty = base * 12
            elif role == "coimbatore_aging":
                qty = base * 95
            elif role == "consistent":
                qty = base * 35
            elif role == "seasonal_summer":
                qty = base * 25
            elif role == "seasonal_winter":
                qty = base * 20
            elif role == "seasonal_schools":
                qty = base * 30
            elif role == "slow_mover":
                qty = base * 80
            elif role == "premium_slow":
                qty = base * 70
            else:
                qty = base * 30
            
            warehouse_stock = WarehouseStock(
                product_id=product.id,
                realm_id=realm_id,
                quantity=int(qty),
            )
            db.add(warehouse_stock)
        
        db.commit()
        print(f"   ✓ Inventory aligned with business story")
        
        print("\n🚚 Creating narrative-driven transfers...")
        transfers = [
            (product_map["FOOD-OIL-SUN"].id, chennai.id, bangalore.id, 450, 
             today - timedelta(days=85), "Emergency transfer during supplier disruption"),
            
            (product_map["FOOD-FLOUR-WH"].id, chennai.id, bangalore.id, 380, 
             today - timedelta(days=82), "Stockout prevention"),
            
            (product_map["CARE-SOAP-BAT"].id, chennai.id, bangalore.id, 850, 
             today - timedelta(days=78), "High-demand product transfer"),
            
            (product_map["SNACK-COOKIES"].id, hyderabad.id, coimbatore.id, 180, 
             today - timedelta(days=25), "Overstock rebalancing"),
            
            (product_map["CARE-CREAM-FAC"].id, hyderabad.id, kochi.id, 95, 
             today - timedelta(days=18), "Overstock distribution"),
            
            (product_map["BABY-POWD-TAL"].id, hyderabad.id, bangalore.id, 110, 
             today - timedelta(days=12), "Rebalancing to high-demand location"),
            
            (product_map["FOOD-RICE-BR5"].id, chennai.id, bangalore.id, 320, 
             today - timedelta(days=3), "Recent replenishment"),
            
            (product_map["BEV-WATER-MIN"].id, chennai.id, bangalore.id, 650, 
             today, "Ongoing stockout prevention"),
        ]
        
        for product_id, from_id, to_id, qty, transfer_date, reason in transfers:
            transfer_cost = Decimal("150") + (Decimal(qty) * Decimal("4.50"))
            transfer = Transfer(
                realm_id=realm_id,
                from_store_id=from_id,
                to_store_id=to_id,
                product_id=product_id,
                quantity=qty,
                transfer_cost=transfer_cost,
                transfer_date=transfer_date,
            )
            db.add(transfer)
        
        db.commit()
        print(f"   ✓ {len(transfers)} transfers with business reasons")
        
        print("\n🎁 Creating donation history...")
        donation_history = [
            (product_map["BEV-JUICE-ORA"].id, "Sunrise Children's Home", "Chennai", 
             "sunrise.home@example.org", today - timedelta(days=15)),
            
            (product_map["SNACK-BISC-CRM"].id, "Hope Bridge Foundation", "Bangalore", 
             "hope.bridge@example.org", today - timedelta(days=12)),
            
            (product_map["BABY-SOAP-MIL"].id, "New Dawn Home", "Hyderabad", 
             "newdawn.home@example.org", today - timedelta(days=8)),
            
            (product_map["FOOD-RICE-WH1"].id, "Little Stars Home", "Kochi", 
             "littlestars.home@example.org", today - timedelta(days=5)),
        ]
        
        for product_id, orphanage, city, email, donation_date in donation_history:
            log = DonationLog(
                realm_id=realm_id,
                product_id=product_id,
                orphanage_name=orphanage,
                orphanage_city=city,
                orphanage_email=email,
                status="sent",
                message=f"Donation notification sent on {donation_date.isoformat()}",
            )
            db.add(log)
        
        db.commit()
        print(f"   ✓ {len(donation_history)} previous donations")
        
        print("\n🔍 Validating system features...")
        analytics = AnalyticsService(db, scope=None)
        overview = analytics.overview()
        
        action_engine = SmartInventoryActionEngine(db, scope=None)
        actions = action_engine.suggestions()
        
        action_counts = {
            "CLEARANCE_SALE": len([a for a in actions if a["action"] == "CLEARANCE_SALE"]),
            "DONATE": len([a for a in actions if a["action"] == "DONATE"]),
            "DISCARD": len([a for a in actions if a["action"] == "DISCARD"]),
        }
        
        print(f"   ✓ Dashboard: {len(overview['kpis'])} KPIs")
        print(f"   ✓ Smart Actions: {len(actions)} total")
        print(f"      - Clearance: {action_counts['CLEARANCE_SALE']}")
        print(f"      - Donate: {action_counts['DONATE']}")
        print(f"      - Discard: {action_counts['DISCARD']}")
        
        print("\n" + "="*70)
        print("✅ NARRATIVE SEED COMPLETE")
        print("="*70)
        
        print("\n📊 BUSINESS STORY:")
        print("   • Supplier disruption (March) → Bangalore stockouts")
        print("   • Emergency transfers from Chennai (April)")
        print("   • Hyderabad over-ordering → Overstock (May)")
        print("   • Inventory aging in Coimbatore")
        print("   • Expiry challenges in Kochi")
        print("   • AI-driven actions across all warehouses")
        
        print("\n🔐 LOGIN:")
        print("   Email: ops@stocklens.com")
        print("   Password: stocklens2024")
        print("   Realm: SL24")
        
        print("\n✨ Every metric tells part of the same story!")
        print("="*70 + "\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

