import random
from datetime import date
from decimal import Decimal
from typing import List


class BusinessEventEngine:
    def __init__(self, config):
        self.config = config
        self.events_triggered = []
        self.rng = random.Random(config.random_seed + 5000)
        self.active_spot_promotions = {}
    
    def check_and_trigger_events(self, day_num: int, current_date: date, inventory_engine, demand_engine, product_specs, warehouse_specs) -> List[str]:
        events = []
        
        if day_num == self.config.summer_promotion_day:
            self._trigger_summer_promotion(demand_engine, product_specs, warehouse_specs)
            events.append("SUMMER_PROMOTION_STARTED")
        
        if day_num == self.config.supplier_disruption_day:
            events.append("SUPPLIER_DISRUPTION_STARTED")
        
        if day_num == self.config.supplier_disruption_day + self.config.disruption_duration:
            events.append("SUPPLIER_DISRUPTION_ENDED")
        
        if day_num == self.config.supplier_disruption_day + 15:
            self._trigger_emergency_transfers(inventory_engine, product_specs, warehouse_specs, current_date)
            events.append("EMERGENCY_TRANSFERS_INITIATED")
        
        if day_num == self.config.clearance_campaign_day:
            events.append("CLEARANCE_CAMPAIGN_STARTED")
        
        if day_num == self.config.donation_campaign_day:
            events.append("DONATION_CAMPAIGN_STARTED")
        
        daily_events = self._trigger_daily_micro_events(day_num, current_date, demand_engine, product_specs, warehouse_specs)
        events.extend(daily_events)
        
        self.events_triggered.extend(events)
        return events
    
    def _trigger_summer_promotion(self, demand_engine, product_specs, warehouse_specs):
        summer_products = ["VEG-TOM-1KG", "VEG-ONI-1KG", "CURD-FRE-500G", "OIL-COC-500ML"]
        for sku in summer_products:
            for warehouse in warehouse_specs:
                demand_engine.activate_promotion(sku, warehouse.name, 1.8, 30)
    
    def _trigger_emergency_transfers(self, inventory_engine, product_specs, warehouse_specs, current_date):
        chennai = next(w for w in warehouse_specs if w.city == "Chennai")
        bangalore = next(w for w in warehouse_specs if w.city == "Bangalore")
        
        critical_skus = ["OIL-SUN-1L", "FLOUR-WHT-5KG", "DAL-TUR-1KG"]
        
        for sku in critical_skus:
            product = next(p for p in product_specs if p.sku == sku)
            transfer_qty = int(product.base_demand * 20)
            transfer_cost = Decimal("150") + (Decimal(transfer_qty) * Decimal("4.5"))
            
            inventory_engine.process_transfer(
                sku,
                chennai.name,
                bangalore.name,
                transfer_qty,
                transfer_cost,
                current_date
            )
    
    def is_supplier_disrupted(self, day_num: int, supplier_id: int) -> bool:
        disruption_start = self.config.supplier_disruption_day
        disruption_end = disruption_start + self.config.disruption_duration
        
        if supplier_id == 1 and disruption_start <= day_num < disruption_end:
            return True
        return False
    
    def _trigger_daily_micro_events(self, day_num: int, current_date: date, demand_engine, product_specs, warehouse_specs) -> List[str]:
        events = []
        
        if day_num < 10:
            return events
        
        if self.rng.random() < 0.15:
            category = self.rng.choice(["Grains", "Pulses", "Oils", "Spices", "Dairy", "Fresh Produce"])
            warehouse = self.rng.choice(warehouse_specs)
            boost = self.rng.uniform(1.3, 1.7)
            
            category_products = [p for p in product_specs if p.category == category]
            if category_products:
                for product in category_products[:self.rng.randint(2, 4)]:
                    demand_engine.activate_promotion(product.sku, warehouse.name, boost, 1)
                events.append(f"SPOT_PROMO_{category}_{warehouse.city}")
        
        if self.rng.random() < 0.08:
            warehouse = self.rng.choice(warehouse_specs)
            premium_products = [p for p in product_specs if p.price_tier == "premium" and self.rng.random() < 0.3]
            boost = self.rng.uniform(1.8, 2.5)
            
            for product in premium_products[:2]:
                demand_engine.activate_promotion(product.sku, warehouse.name, boost, 1)
            events.append(f"LOCAL_DEMAND_SPIKE_{warehouse.city}")
        
        if current_date.day == 1 or current_date.day == 15:
            value_products = [p for p in product_specs if p.price_tier == "value"]
            selected = self.rng.sample(value_products, min(6, len(value_products)))
            boost = 1.4
            
            for product in selected:
                for warehouse in warehouse_specs:
                    demand_engine.activate_promotion(product.sku, warehouse.name, boost, 3)
            events.append("PAYDAY_VALUE_BOOST")
        
        if current_date.weekday() == 4 and self.rng.random() < 0.25:
            weekend_categories = ["Fresh Produce", "Dairy", "Ready to Eat"]
            selected_category = self.rng.choice(weekend_categories)
            products = [p for p in product_specs if p.category == selected_category]
            
            for product in self.rng.sample(products, min(4, len(products))):
                for warehouse in warehouse_specs:
                    demand_engine.activate_promotion(product.sku, warehouse.name, 1.35, 3)
            events.append(f"WEEKEND_PROMO_{selected_category}")
        
        return events
