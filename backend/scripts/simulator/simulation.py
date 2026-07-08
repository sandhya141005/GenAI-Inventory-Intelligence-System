from datetime import date, timedelta
from typing import Dict, List
from decimal import Decimal

from .config import SimulationConfig
from .generators import CompanyGenerator
from .demand_engine import DemandEngine
from .inventory_engine import InventoryEngine
from .event_engine import BusinessEventEngine


class DailySimulationEngine:
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.company_gen = CompanyGenerator(config.random_seed)
        self.demand_engine = DemandEngine(config.random_seed, config)
        self.inventory_engine = InventoryEngine(config.random_seed)
        self.event_engine = BusinessEventEngine(config)
        
        self.product_specs = self.company_gen.generate_products()
        self.warehouse_specs = self.company_gen.generate_warehouses()
        self.supplier_specs = self.company_gen.generate_suppliers(
            config.supplier_disruption_day,
            config.disruption_duration
        )
        self.orphanages = self.company_gen.generate_orphanages()
        
        self.inventory_engine.initialize_inventory(self.product_specs, self.warehouse_specs)
    
    def run_simulation(self) -> Dict:
        print(f"\n🔄 Running {self.config.simulation_days}-day business simulation...")
        
        for day_num in range(self.config.simulation_days):
            current_date = self.config.start_date + timedelta(days=day_num)
            self._simulate_day(day_num, current_date)
            
            if day_num % 30 == 0:
                print(f"   Day {day_num}: {current_date.isoformat()}")
        
        print(f"   ✓ Simulation complete")
        
        return {
            "product_specs": self.product_specs,
            "warehouse_specs": self.warehouse_specs,
            "supplier_specs": self.supplier_specs,
            "orphanages": self.orphanages,
            "inventory_state": self.inventory_engine.state,
            "events_triggered": self.event_engine.events_triggered,
        }
    
    def _simulate_day(self, day_num: int, current_date: date):
        self.inventory_engine.process_pending_shipments(current_date)
        
        events = self.event_engine.check_and_trigger_events(
            day_num,
            current_date,
            self.inventory_engine,
            self.demand_engine,
            self.product_specs,
            self.warehouse_specs
        )
        
        for product in self.product_specs:
            for warehouse in self.warehouse_specs:
                supplier_disrupted = self.event_engine.is_supplier_disrupted(day_num, product.supplier_id)
                
                demand = self.demand_engine.calculate_demand(
                    product,
                    warehouse,
                    current_date,
                    day_num,
                    supplier_disrupted
                )
                
                self.inventory_engine.process_sales(
                    product.sku,
                    warehouse.name,
                    demand,
                    product.price,
                    current_date
                )
        
        if day_num > 20 and day_num % 7 == 0:
            self._check_opportunistic_transfers(current_date)
        
        for product in self.product_specs:
            for warehouse in self.warehouse_specs:
                if self.event_engine.is_supplier_disrupted(day_num, product.supplier_id):
                    continue
                
                reorder_qty = self.inventory_engine.check_replenishment_needed(
                    product.sku,
                    warehouse.name,
                    product.base_demand,
                    warehouse.replenishment_aggressiveness
                )
                
                if reorder_qty > 0:
                    supplier = next(s for s in self.supplier_specs if s.supplier_id == product.supplier_id)
                    arrival_date = current_date + timedelta(days=supplier.lead_time_days)
                    
                    self.inventory_engine.schedule_shipment(
                        product.sku,
                        warehouse.name,
                        reorder_qty,
                        arrival_date,
                        supplier.supplier_id
                    )
    
    def _check_opportunistic_transfers(self, current_date: date):
        chennai = next(w for w in self.warehouse_specs if w.city == "Chennai")
        
        for product in self.product_specs:
            for warehouse in self.warehouse_specs:
                if warehouse.city == "Chennai":
                    continue
                
                current_stock = self.inventory_engine.state.get_stock(product.sku, warehouse.name)
                critical_level = product.base_demand * 5
                
                if current_stock < critical_level:
                    chennai_stock = self.inventory_engine.state.get_stock(product.sku, chennai.name)
                    
                    if chennai_stock > product.base_demand * 25:
                        transfer_qty = int(product.base_demand * 10)
                        transfer_cost = Decimal("120") + (Decimal(transfer_qty) * Decimal("3.8"))
                        
                        self.inventory_engine.process_transfer(
                            product.sku,
                            chennai.name,
                            warehouse.name,
                            transfer_qty,
                            transfer_cost,
                            current_date
                        )
                        return
