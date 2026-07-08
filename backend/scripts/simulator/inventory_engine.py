from collections import defaultdict
from datetime import date, timedelta
from typing import Dict, List, Tuple
from decimal import Decimal


class InventoryState:
    def __init__(self):
        self.stock: Dict[Tuple[str, str], int] = defaultdict(int)
        self.pending_shipments: List[dict] = []
        self.stockout_events: List[dict] = []
        self.sales_history: List[dict] = []
        self.transfer_history: List[dict] = []
    
    def get_stock(self, sku: str, warehouse: str) -> int:
        return self.stock[(sku, warehouse)]
    
    def set_stock(self, sku: str, warehouse: str, quantity: int):
        self.stock[(sku, warehouse)] = max(0, quantity)
    
    def add_stock(self, sku: str, warehouse: str, quantity: int):
        current = self.get_stock(sku, warehouse)
        self.set_stock(sku, warehouse, current + quantity)
    
    def remove_stock(self, sku: str, warehouse: str, quantity: int) -> int:
        current = self.get_stock(sku, warehouse)
        actual_sold = min(current, quantity)
        self.set_stock(sku, warehouse, current - actual_sold)
        return actual_sold


class InventoryEngine:
    def __init__(self, seed: int):
        self.state = InventoryState()
        self.replenishment_threshold = 0.3
    
    def initialize_inventory(self, product_specs, warehouse_specs):
        for product in product_specs:
            for warehouse in warehouse_specs:
                effective_demand = product.base_demand
                
                effective_demand *= warehouse.demand_multiplier
                
                category_pref = warehouse.category_preferences.get(product.category, 1.0)
                effective_demand *= category_pref
                
                if product.warehouse_affinity == warehouse.city.lower():
                    days_of_stock = 60
                elif product.warehouse_affinity == "all":
                    days_of_stock = 45
                elif warehouse.personality == "overstock":
                    days_of_stock = 90
                elif warehouse.personality == "healthy_hub":
                    days_of_stock = 50
                else:
                    days_of_stock = 35
                
                initial_stock = int(effective_demand * days_of_stock)
                self.state.set_stock(product.sku, warehouse.name, max(0, initial_stock))
    
    def process_sales(self, sku: str, warehouse_name: str, demand: int, product_price: Decimal, current_date: date) -> Tuple[int, Decimal]:
        actual_sold = self.state.remove_stock(sku, warehouse_name, demand)
        revenue = product_price * Decimal(actual_sold)
        
        self.state.sales_history.append({
            "sku": sku,
            "warehouse": warehouse_name,
            "date": current_date,
            "quantity": actual_sold,
            "revenue": revenue,
        })
        
        if actual_sold < demand:
            lost_sales = demand - actual_sold
            lost_revenue = product_price * Decimal(lost_sales)
            self.state.stockout_events.append({
                "sku": sku,
                "warehouse": warehouse_name,
                "date": current_date,
                "lost_sales": lost_sales,
                "lost_revenue": lost_revenue,
            })
        
        return actual_sold, revenue
    
    def receive_shipment(self, sku: str, warehouse_name: str, quantity: int, current_date: date):
        self.state.add_stock(sku, warehouse_name, quantity)
    
    def process_transfer(self, sku: str, from_warehouse: str, to_warehouse: str, quantity: int, transfer_cost: Decimal, current_date: date):
        current = self.state.get_stock(sku, from_warehouse)
        actual_transfer = min(current, quantity)
        
        if actual_transfer > 0:
            self.state.remove_stock(sku, from_warehouse, actual_transfer)
            self.state.add_stock(sku, to_warehouse, actual_transfer)
            
            self.state.transfer_history.append({
                "sku": sku,
                "from_warehouse": from_warehouse,
                "to_warehouse": to_warehouse,
                "quantity": actual_transfer,
                "transfer_cost": transfer_cost,
                "date": current_date,
            })
    
    def check_replenishment_needed(self, sku: str, warehouse_name: str, base_demand: int, replenishment_aggressiveness: float) -> int:
        current_stock = self.state.get_stock(sku, warehouse_name)
        target_stock = int(base_demand * 30 * replenishment_aggressiveness)
        
        if current_stock < target_stock * self.replenishment_threshold:
            reorder_qty = target_stock - current_stock
            return max(0, reorder_qty)
        return 0
    
    def schedule_shipment(self, sku: str, warehouse_name: str, quantity: int, arrival_date: date, supplier_id: int):
        self.state.pending_shipments.append({
            "sku": sku,
            "warehouse": warehouse_name,
            "quantity": quantity,
            "arrival_date": arrival_date,
            "supplier_id": supplier_id,
        })
    
    def process_pending_shipments(self, current_date: date):
        arriving_today = [s for s in self.state.pending_shipments if s["arrival_date"] == current_date]
        
        for shipment in arriving_today:
            self.receive_shipment(shipment["sku"], shipment["warehouse"], shipment["quantity"], current_date)
        
        self.state.pending_shipments = [s for s in self.state.pending_shipments if s["arrival_date"] > current_date]
