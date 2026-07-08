from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.analytics_data import Product, Store, WarehouseStock, Sale, Transfer, DonationLog
from app.models.user import Realm, User, STORE_MANAGER, WAREHOUSE_OWNER
from app.core.security import hash_password


class DatabasePersistence:
    def __init__(self, db: Session):
        self.db = db
    
    def clear_existing_data(self):
        print("\n🗑️  Clearing existing data...")
        for user in self.db.query(User).filter(User.assigned_store_id.isnot(None)).all():
            user.assigned_store_id = None
        self.db.commit()
        
        self.db.query(DonationLog).delete()
        self.db.query(Sale).delete()
        self.db.query(Transfer).delete()
        self.db.query(WarehouseStock).delete()
        self.db.query(Product).delete()
        self.db.query(Store).delete()
        self.db.commit()
    
    def create_realm_and_owner(self):
        email = "ops@stocklens.com"
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            user = User(
                email=email,
                full_name="Operations Director",
                hashed_password=hash_password("stocklens2024"),
                is_active=True,
                role=WAREHOUSE_OWNER,
            )
            self.db.add(user)
            self.db.flush()
        
        realm = self.db.query(Realm).filter(Realm.join_code == "SL24").first()
        if not realm:
            realm = Realm(
                name="StockLens Retail Network",
                industry_tag="Retail Distribution",
                join_code="SL24",
                owner_user_id=user.id,
            )
            self.db.add(realm)
            self.db.flush()
        
        user.realm_id = realm.id
        user.role = WAREHOUSE_OWNER
        self.db.commit()
        self.db.refresh(user)
        
        return user.id, realm.id
    
    def persist_simulation_results(self, simulation_results: dict, realm_id: int, end_date: date):
        print("\n💾 Persisting simulation results to database...")
        
        warehouse_specs = simulation_results["warehouse_specs"]
        product_specs = simulation_results["product_specs"]
        inventory_state = simulation_results["inventory_state"]
        orphanages = simulation_results["orphanages"]
        
        print("   Creating warehouses...")
        store_map = {}
        for warehouse_spec in warehouse_specs:
            store = Store(
                realm_id=realm_id,
                name=warehouse_spec.name,
                city=warehouse_spec.city,
                region=warehouse_spec.region,
                store_type=warehouse_spec.store_type,
            )
            self.db.add(store)
            self.db.flush()
            store_map[warehouse_spec.name] = store
        self.db.commit()
        
        bangalore_store = store_map.get("Bangalore Metro")
        hyderabad_store = store_map.get("Hyderabad Central")
        
        if bangalore_store:
            self._create_store_manager(realm_id, "bangalore.ops@stocklens.com", "Bangalore Operations Manager", bangalore_store.id)
        if hyderabad_store:
            self._create_store_manager(realm_id, "hyderabad.ops@stocklens.com", "Hyderabad Inventory Manager", hyderabad_store.id)
        
        print("   Creating products...")
        product_map = {}
        for product_spec in product_specs:
            expiry_date = None
            if product_spec.expiry_days is not None:
                if product_spec.warehouse_affinity == "kochi" and product_spec.category in ["Beverages", "Medicine"]:
                    if product_spec.sku in ["BEV-MILK-TET", "MED-VITA-MULT"]:
                        expiry_date = end_date - timedelta(days=2)
                    else:
                        expiry_date = end_date + timedelta(days=4)
                else:
                    expiry_date = end_date + timedelta(days=product_spec.expiry_days)
            
            product = Product(
                realm_id=realm_id,
                sku=product_spec.sku,
                name=product_spec.name,
                category=product_spec.category,
                price=product_spec.price,
                cost=product_spec.cost,
                expiry_date=expiry_date,
            )
            self.db.add(product)
            self.db.flush()
            product_map[product_spec.sku] = product
        self.db.commit()
        
        print("   Creating inventory records...")
        consolidated_stock = {}
        for (sku, warehouse_name), quantity in inventory_state.stock.items():
            product = product_map.get(sku)
            if product:
                if product.id not in consolidated_stock:
                    consolidated_stock[product.id] = 0
                consolidated_stock[product.id] += quantity
        
        for product_id, total_quantity in consolidated_stock.items():
            warehouse_stock = WarehouseStock(
                product_id=product_id,
                realm_id=realm_id,
                quantity=total_quantity,
            )
            self.db.add(warehouse_stock)
        self.db.commit()
        
        print(f"   Creating {len(inventory_state.sales_history)} sales records...")
        for sale_record in inventory_state.sales_history:
            product = product_map.get(sale_record["sku"])
            store = store_map.get(sale_record["warehouse"])
            if product and store:
                sale = Sale(
                    realm_id=realm_id,
                    product_id=product.id,
                    store_id=store.id,
                    quantity=sale_record["quantity"],
                    revenue=sale_record["revenue"],
                    sale_date=sale_record["date"],
                )
                self.db.add(sale)
        
        if len(inventory_state.sales_history) > 1000:
            self.db.flush()
        self.db.commit()
        
        print(f"   Creating {len(inventory_state.transfer_history)} transfers...")
        for transfer_record in inventory_state.transfer_history:
            product = product_map.get(transfer_record["sku"])
            from_store = store_map.get(transfer_record["from_warehouse"])
            to_store = store_map.get(transfer_record["to_warehouse"])
            
            if product and from_store and to_store:
                transfer = Transfer(
                    realm_id=realm_id,
                    from_store_id=from_store.id,
                    to_store_id=to_store.id,
                    product_id=product.id,
                    quantity=transfer_record["quantity"],
                    transfer_cost=transfer_record["transfer_cost"],
                    transfer_date=transfer_record["date"],
                )
                self.db.add(transfer)
        self.db.commit()
        
        print("   Creating donation history...")
        self._create_donation_history(realm_id, product_map, orphanages, end_date)
        
        print("   ✓ All data persisted")
    
    def _create_store_manager(self, realm_id: int, email: str, name: str, store_id: int):
        manager = self.db.query(User).filter(User.email == email).first()
        if not manager:
            manager = User(
                email=email,
                full_name=name,
                hashed_password=hash_password("stocklens2024"),
                is_active=True,
            )
            self.db.add(manager)
        manager.realm_id = realm_id
        manager.role = STORE_MANAGER
        manager.assigned_store_id = store_id
        self.db.commit()
    
    def _create_donation_history(self, realm_id: int, product_map: dict, orphanages: list, end_date: date):
        donation_products = [
            ("RICE-WHT-1KG", orphanages[0], end_date - timedelta(days=15)),
            ("DAL-TUR-1KG", orphanages[1], end_date - timedelta(days=12)),
            ("OIL-SUN-1L", orphanages[2], end_date - timedelta(days=8)),
            ("FLOUR-WHT-5KG", orphanages[3], end_date - timedelta(days=5)),
        ]
        
        for sku, orphanage, donation_date in donation_products:
            product = product_map.get(sku)
            if product:
                log = DonationLog(
                    realm_id=realm_id,
                    product_id=product.id,
                    orphanage_name=orphanage["name"],
                    orphanage_city=orphanage["city"],
                    orphanage_email=orphanage["email"],
                    status="sent",
                    message=f"Donation notification sent on {donation_date.isoformat()}",
                )
                self.db.add(log)
        self.db.commit()
