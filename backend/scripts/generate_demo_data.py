"""
McKinsey Executive Demo Data Generator
Generates realistic automotive inventory data with coherent business relationships
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import date, timedelta
from decimal import Decimal
import random

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.analytics_data import Product, Store, WarehouseStock, Sale, Transfer
from app.models.user import Realm, STORE_MANAGER, WAREHOUSE_OWNER, User
from app.core.security import hash_password


# Automotive Product Categories and realistic pricing
AUTOMOTIVE_PRODUCTS = [
    # Engine Components
    ("ENG-OIL-5W30-5L", "Engine Oil 5W-30 5L", "Engine Oil", Decimal("45.00"), Decimal("28.00")),
    ("ENG-OIL-10W40-5L", "Engine Oil 10W-40 5L", "Engine Oil", Decimal("42.00"), Decimal("26.00")),
    ("ENG-FILTER-STD", "Engine Oil Filter Standard", "Filters", Decimal("12.50"), Decimal("7.00")),
    ("ENG-FILTER-PREM", "Engine Oil Filter Premium", "Filters", Decimal("18.00"), Decimal("10.00")),
    ("AIR-FILTER-STD", "Air Filter Standard", "Filters", Decimal("15.00"), Decimal("8.50")),
    ("AIR-FILTER-PREM", "Air Filter Premium", "Filters", Decimal("22.00"), Decimal("12.00")),
    ("FUEL-FILTER-DSL", "Fuel Filter Diesel", "Filters", Decimal("14.00"), Decimal("8.00")),
    ("FUEL-FILTER-PTL", "Fuel Filter Petrol", "Filters", Decimal("13.00"), Decimal("7.50")),
    
    # Brake Components
    ("BRK-PAD-FRONT-STD", "Brake Pad Set Front Standard", "Brakes", Decimal("65.00"), Decimal("38.00")),
    ("BRK-PAD-FRONT-PREM", "Brake Pad Set Front Premium", "Brakes", Decimal("95.00"), Decimal("55.00")),
    ("BRK-PAD-REAR-STD", "Brake Pad Set Rear Standard", "Brakes", Decimal("58.00"), Decimal("34.00")),
    ("BRK-PAD-REAR-PREM", "Brake Pad Set Rear Premium", "Brakes", Decimal("88.00"), Decimal("52.00")),
    ("BRK-DISC-FRONT", "Brake Disc Front Pair", "Brakes", Decimal("120.00"), Decimal("72.00")),
    ("BRK-DISC-REAR", "Brake Disc Rear Pair", "Brakes", Decimal("110.00"), Decimal("66.00")),
    ("BRK-FLUID-DOT4", "Brake Fluid DOT4 1L", "Fluids", Decimal("8.50"), Decimal("5.00")),
    
    # Suspension & Steering
    ("SUS-SHOCK-FRONT-L", "Front Shock Absorber Left", "Suspension", Decimal("85.00"), Decimal("50.00")),
    ("SUS-SHOCK-FRONT-R", "Front Shock Absorber Right", "Suspension", Decimal("85.00"), Decimal("50.00")),
    ("SUS-SHOCK-REAR-L", "Rear Shock Absorber Left", "Suspension", Decimal("78.00"), Decimal("46.00")),
    ("SUS-SHOCK-REAR-R", "Rear Shock Absorber Right", "Suspension", Decimal("78.00"), Decimal("46.00")),
    ("SUS-SPRING-FRONT", "Coil Spring Front", "Suspension", Decimal("55.00"), Decimal("32.00")),
    ("SUS-SPRING-REAR", "Coil Spring Rear", "Suspension", Decimal("52.00"), Decimal("30.00")),
    
    # Electrical Components
    ("ELEC-BATTERY-60AH", "Car Battery 60Ah", "Electrical", Decimal("95.00"), Decimal("58.00")),
    ("ELEC-BATTERY-70AH", "Car Battery 70Ah", "Electrical", Decimal("115.00"), Decimal("70.00")),
    ("ELEC-BATTERY-90AH", "Car Battery 90Ah", "Electrical", Decimal("145.00"), Decimal("88.00")),
    ("ELEC-SPARK-PLUG", "Spark Plug Set (4pcs)", "Electrical", Decimal("28.00"), Decimal("16.00")),
    ("ELEC-ALTERNATOR-80A", "Alternator 80A", "Electrical", Decimal("180.00"), Decimal("110.00")),
    ("ELEC-STARTER-MOTOR", "Starter Motor", "Electrical", Decimal("165.00"), Decimal("100.00")),
    ("ELEC-HEADLIGHT-LED", "LED Headlight Bulb Pair", "Electrical", Decimal("42.00"), Decimal("24.00")),
    
    # Tyres & Wheels
    ("TYRE-165-80-R14", "Tyre 165/80 R14", "Tyres", Decimal("68.00"), Decimal("42.00")),
    ("TYRE-185-65-R15", "Tyre 185/65 R15", "Tyres", Decimal("85.00"), Decimal("52.00")),
    ("TYRE-195-55-R16", "Tyre 195/55 R16", "Tyres", Decimal("105.00"), Decimal("64.00")),
    ("TYRE-205-55-R16", "Tyre 205/55 R16", "Tyres", Decimal("115.00"), Decimal("70.00")),
    ("TYRE-215-60-R17", "Tyre 215/60 R17 SUV", "Tyres", Decimal("135.00"), Decimal("82.00")),
    
    # Cooling System
    ("COOL-RADIATOR-STD", "Radiator Standard", "Cooling", Decimal("95.00"), Decimal("58.00")),
    ("COOL-THERMOSTAT", "Engine Thermostat", "Cooling", Decimal("18.00"), Decimal("11.00")),
    ("COOL-WATERPUMP", "Water Pump", "Cooling", Decimal("65.00"), Decimal("40.00")),
    ("COOL-HOSE-KIT", "Radiator Hose Kit", "Cooling", Decimal("32.00"), Decimal("19.00")),
    ("COOL-COOLANT-5L", "Engine Coolant 5L", "Fluids", Decimal("25.00"), Decimal("15.00")),
    
    # Belts & Chains
    ("BELT-TIMING-KIT", "Timing Belt Kit", "Belts", Decimal("85.00"), Decimal("52.00")),
    ("BELT-SERPENTINE", "Serpentine Belt", "Belts", Decimal("28.00"), Decimal("17.00")),
    ("BELT-ALTERNATOR", "Alternator Belt", "Belts", Decimal("15.00"), Decimal("9.00")),
    
    # Wipers & Lighting
    ("WIPER-BLADE-24", "Wiper Blade 24 inch", "Accessories", Decimal("12.00"), Decimal("7.00")),
    ("WIPER-BLADE-18", "Wiper Blade 18 inch", "Accessories", Decimal("10.00"), Decimal("6.00")),
    ("BULB-H7-HALOGEN", "H7 Halogen Bulb", "Electrical", Decimal("8.00"), Decimal("5.00")),
    ("BULB-H4-HALOGEN", "H4 Halogen Bulb", "Electrical", Decimal("9.00"), Decimal("5.50")),
    
    # Clutch Components
    ("CLUTCH-KIT-STD", "Clutch Kit Standard", "Clutch", Decimal("155.00"), Decimal("95.00")),
    ("CLUTCH-KIT-HEAVY", "Clutch Kit Heavy Duty", "Clutch", Decimal("195.00"), Decimal("120.00")),
    
    # Exhaust Components
    ("EXH-MUFFLER", "Exhaust Muffler", "Exhaust", Decimal("125.00"), Decimal("75.00")),
    ("EXH-CATALYTIC-CONV", "Catalytic Converter", "Exhaust", Decimal("285.00"), Decimal("175.00")),
    ("EXH-GASKET-SET", "Exhaust Gasket Set", "Exhaust", Decimal("18.00"), Decimal("11.00")),
    
    # Body & Interior
    ("BODY-SIDE-MIRROR-L", "Side Mirror Left", "Body Parts", Decimal("45.00"), Decimal("28.00")),
    ("BODY-SIDE-MIRROR-R", "Side Mirror Right", "Body Parts", Decimal("45.00"), Decimal("28.00")),
    ("INT-CABIN-FILTER", "Cabin Air Filter", "Filters", Decimal("15.00"), Decimal("9.00")),
    
    # Additional high-value items
    ("TRANS-OIL-ATF-4L", "Transmission Oil ATF 4L", "Fluids", Decimal("38.00"), Decimal("23.00")),
    ("WHEEL-BEARING-FRONT", "Wheel Bearing Front", "Suspension", Decimal("42.00"), Decimal("26.00")),
    ("WHEEL-BEARING-REAR", "Wheel Bearing Rear", "Suspension", Decimal("38.00"), Decimal("23.00")),
]

# Store/Warehouse locations with realistic characteristics
# Fields: name, city, region, store_type (matching Store model)
STORES = [
    ("Delhi Central Hub", "Delhi", "North", "hub"),
    ("Mumbai West", "Mumbai", "West", "store"),
    ("Mumbai East", "Mumbai", "West", "store"),
    ("Bangalore South", "Bangalore", "South", "store"),
    ("Bangalore North", "Bangalore", "South", "store"),
    ("Chennai Central", "Chennai", "South", "store"),
    ("Hyderabad Tech City", "Hyderabad", "South", "store"),
    ("Pune Market", "Pune", "West", "store"),
    ("Kolkata Downtown", "Kolkata", "East", "store"),
    ("Ahmedabad Industrial", "Ahmedabad", "West", "store"),
]


def generate_realistic_demand_profile(category: str, season_factor: float = 1.0) -> dict:
    """Generate demand characteristics based on product category"""
    
    # Base daily demand patterns by category
    demand_profiles = {
        "Engine Oil": {"base": 25, "volatility": 0.15, "seasonal": True},
        "Filters": {"base": 35, "volatility": 0.12, "seasonal": False},
        "Brakes": {"base": 18, "volatility": 0.20, "seasonal": False},
        "Tyres": {"base": 12, "volatility": 0.25, "seasonal": True},
        "Electrical": {"base": 15, "volatility": 0.18, "seasonal": False},
        "Suspension": {"base": 10, "volatility": 0.22, "seasonal": False},
        "Fluids": {"base": 20, "volatility": 0.15, "seasonal": True},
        "Cooling": {"base": 14, "volatility": 0.20, "seasonal": True},
        "Belts": {"base": 16, "volatility": 0.18, "seasonal": False},
        "Accessories": {"base": 30, "volatility": 0.10, "seasonal": False},
        "Clutch": {"base": 8, "volatility": 0.25, "seasonal": False},
        "Exhaust": {"base": 6, "volatility": 0.30, "seasonal": False},
        "Body Parts": {"base": 12, "volatility": 0.22, "seasonal": False},
    }
    
    profile = demand_profiles.get(category, {"base": 15, "volatility": 0.20, "seasonal": False})
    
    if profile["seasonal"]:
        profile["base"] = int(profile["base"] * season_factor)
    
    return profile


def create_demo_user(db: Session) -> tuple[int, int]:
    """Create demo owner and realm if not exists."""
    demo_email = "demo@mckinsey.com"
    user = db.query(User).filter(User.email == demo_email).first()

    if not user:
        user = User(
            email=demo_email,
            full_name="McKinsey Demo User",
            hashed_password=hash_password("demo1234"),
            is_active=True,
            role=WAREHOUSE_OWNER,
        )
        db.add(user)
        db.flush()
        print(f"Created demo owner: {demo_email} / demo1234")
    else:
        print(f"Demo owner already exists: {demo_email}")

    realm = db.query(Realm).filter(Realm.join_code == "8341").first()
    if not realm:
        realm = Realm(
            name="StockLens Automotive Demo",
            industry_tag="Automotive Parts",
            join_code="8341",
            owner_user_id=user.id,
        )
        db.add(realm)
        db.flush()

    user.realm_id = realm.id
    user.role = WAREHOUSE_OWNER
    db.commit()
    db.refresh(user)

    return user.id, realm.id


def create_demo_managers(db: Session, realm_id: int, store_objects: list[Store]) -> None:
    manager_specs = [
        ("chennai.manager@stocklens.local", "Chennai Store Manager", store_objects[5].id),
        ("mumbai.manager@stocklens.local", "Mumbai Store Manager", store_objects[1].id),
        ("unassigned.manager@stocklens.local", "Unassigned Store Manager", None),
    ]
    for email, full_name, store_id in manager_specs:
        manager = db.query(User).filter(User.email == email).first()
        if not manager:
            manager = User(
                email=email,
                full_name=full_name,
                hashed_password=hash_password("demo1234"),
                is_active=True,
            )
            db.add(manager)
        manager.realm_id = realm_id
        manager.role = STORE_MANAGER
        manager.assigned_store_id = store_id
    db.commit()


def generate_demo_data():
    """Generate complete demo dataset"""
    db = SessionLocal()
    
    try:
        print("🚀 Starting McKinsey Executive Demo Data Generation...")
        print("=" * 60)
        
        # Clear existing data
        print("\n🗑️  Clearing existing data...")
        db.query(Sale).delete()
        db.query(Transfer).delete()
        db.query(WarehouseStock).delete()
        db.query(Product).delete()
        db.query(Store).delete()
        db.commit()
        
        # Create demo owner and realm
        _, realm_id = create_demo_user(db)
        
        # Create stores (matching Store model: name, city, region, store_type)
        print("\n🏪 Creating stores and warehouses...")
        store_objects = []
        for name, city, region, store_type in STORES:
            store = Store(
                realm_id=realm_id,
                name=name,
                city=city,
                region=region,
                store_type=store_type
            )
            db.add(store)
            store_objects.append(store)
        db.commit()
        print(f"Created {len(store_objects)} stores")
        create_demo_managers(db, realm_id, store_objects)
        
        today = date.today()

        # Create products
        print("\n📦 Creating automotive products...")
        product_objects = []
        perishable_categories = {"Engine Oil", "Fluids", "Cooling"}
        expiry_offsets = [-4, 5, 12, 24, 45, 90]
        perishable_index = 0

        for sku, name, category, price, cost in AUTOMOTIVE_PRODUCTS:
            expiry_date = None
            if category in perishable_categories:
                expiry_date = today + timedelta(days=expiry_offsets[perishable_index % len(expiry_offsets)])
                perishable_index += 1

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
            product_objects.append(product)
        db.commit()
        print(f"✅ Created {len(product_objects)} products")
        
        # Generate inventory with realistic distribution
        print("\n📊 Generating warehouse inventory...")
        # Warehouse stock only has product_id and quantity (no last_updated field)
        for product in product_objects:
            demand_profile = generate_realistic_demand_profile(product.category)
            base_demand = demand_profile["base"]
            
            # Warehouse stock: 30-60 days of supply for most items
            # Some items intentionally low (stockout risk)
            # Some items high (overstock)
            
            stock_scenarios = random.choices(
                ["normal", "low", "high"],
                weights=[0.70, 0.20, 0.10],
                k=1
            )[0]
            
            if stock_scenarios == "low":
                quantity = int(base_demand * random.uniform(5, 15))  # 5-15 days
            elif stock_scenarios == "high":
                quantity = int(base_demand * random.uniform(80, 120))  # 80-120 days
            else:
                quantity = int(base_demand * random.uniform(30, 60))  # 30-60 days
            
            warehouse_stock = WarehouseStock(
                product_id=product.id,
                realm_id=realm_id,
                quantity=quantity
            )
            db.add(warehouse_stock)
        
        db.commit()
        print(f"✅ Generated warehouse inventory")
        
        # Generate 90 days of sales history
        print("\n💰 Generating sales history (90 days)...")
        
        sales_count = 0
        start_date = today - timedelta(days=90)
        
        for day_offset in range(90):
            current_date = start_date + timedelta(days=day_offset)
            
            # Weekend factor (lower sales on weekends)
            is_weekend = current_date.weekday() >= 5
            weekend_factor = 0.6 if is_weekend else 1.0
            
            # Seasonal factor (simulate monsoon/summer variations)
            month = current_date.month
            if month in [6, 7, 8, 9]:  # Monsoon season
                seasonal_factor = 1.3  # Higher demand for wipers, brakes
            elif month in [4, 5]:  # Summer
                seasonal_factor = 1.2  # Higher demand for coolant, AC parts
            else:
                seasonal_factor = 1.0
            
            # Generate sales for subset of products each day
            products_to_sell = random.sample(product_objects, k=random.randint(25, 45))
            
            for product in products_to_sell:
                demand_profile = generate_realistic_demand_profile(
                    product.category,
                    seasonal_factor
                )
                
                base_demand = demand_profile["base"]
                volatility = demand_profile["volatility"]
                
                # Distribute sales across 2-4 stores
                num_stores = random.randint(2, 4)
                selling_stores = random.sample(store_objects[1:], num_stores)  # Exclude warehouse
                
                for store in selling_stores:
                    # Calculate daily quantity with realistic variation
                    daily_qty = max(
                        0,
                        int(base_demand * weekend_factor * random.gauss(1.0, volatility))
                    )
                    
                    if daily_qty > 0:
                        revenue = product.price * Decimal(daily_qty)
                        
                        sale = Sale(
                            realm_id=realm_id,
                            product_id=product.id,
                            store_id=store.id,
                            quantity=daily_qty,
                            revenue=revenue,
                            sale_date=current_date
                        )
                        db.add(sale)
                        sales_count += 1
        
        db.commit()
        print(f"✅ Generated {sales_count} sales transactions")
        
        # Generate inventory transfers (realistic scenarios)
        # Transfer model has: from_store_id, to_store_id, product_id, quantity, transfer_cost, transfer_date
        print("\n🚚 Generating inventory transfers...")
        
        transfer_scenarios = [
            # Stockout prevention transfers
            ("BRK-PAD-FRONT-STD", store_objects[2], store_objects[1], 45, today - timedelta(days=3)),
            ("TYRE-185-65-R15", store_objects[3], store_objects[4], 28, today - timedelta(days=5)),
            ("ENG-OIL-5W30-5L", store_objects[5], store_objects[6], 120, today - timedelta(days=7)),
            
            # Overstock rebalancing
            ("ELEC-BATTERY-70AH", store_objects[7], store_objects[8], 18, today - timedelta(days=10)),
            ("CLUTCH-KIT-STD", store_objects[4], store_objects[2], 12, today - timedelta(days=12)),
            
            # Recent transfers (in-transit)
            ("AIR-FILTER-STD", store_objects[3], store_objects[5], 65, today - timedelta(days=1)),
            ("WIPER-BLADE-24", store_objects[6], store_objects[7], 85, today),
        ]
        
        for sku, from_store, to_store, qty, transfer_date in transfer_scenarios:
            product = next((p for p in product_objects if p.sku == sku), None)
            if product:
                # Calculate transfer cost (approx INR 2 per unit + INR 50 base cost)
                transfer_cost = Decimal("50.00") + (Decimal(qty) * Decimal("2.00"))
                
                transfer = Transfer(
                    realm_id=realm_id,
                    from_store_id=from_store.id,
                    to_store_id=to_store.id,
                    product_id=product.id,
                    quantity=qty,
                    transfer_cost=transfer_cost,
                    transfer_date=transfer_date
                )
                db.add(transfer)
        
        db.commit()
        print(f"✅ Generated {len(transfer_scenarios)} transfers")
        
        # Summary statistics
        print("\n" + "=" * 60)
        print("📈 DEMO DATA GENERATION COMPLETE")
        print("=" * 60)
        print(f"✅ Products: {len(product_objects)}")
        print(f"✅ Stores/Warehouses: {len(store_objects)}")
        print(f"✅ Warehouse Stock Records: {len(product_objects)}")
        print(f"✅ Sales Transactions: {sales_count}")
        print(f"✅ Transfers: {len(transfer_scenarios)}")
        print(f"✅ Date Range: {start_date} to {today}")
        print("\n🎯 Expected Analytics Outcomes:")
        print("   • 15-20% of products with stockout risk")
        print("   • 8-12% of products overstocked")
        print("   • Significant revenue at risk from stockouts")
        print("   • Multiple transfer opportunities")
        print("   • Realistic aging inventory patterns")
        print("   • Believable seasonal demand variations")
        print("\n🔐 Demo Credentials:")
        print("   Email: demo@mckinsey.com")
        print("   Password: demo1234")
        print("\n✨ Ready for McKinsey Executive Demo!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error generating demo data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    generate_demo_data()
