import random
from datetime import date
from typing import Dict, Tuple


class DemandEngine:
    def __init__(self, seed: int, config):
        self.rng = random.Random(seed + 1000)
        self.config = config
        self.active_promotions = {}
    
    def calculate_demand(
        self,
        product_spec,
        warehouse_spec,
        current_date: date,
        day_num: int,
        supplier_disrupted: bool
    ) -> int:
        base = product_spec.base_demand
        
        base *= warehouse_spec.demand_multiplier
        
        category_pref = warehouse_spec.category_preferences.get(product_spec.category, 1.0)
        base *= category_pref
        
        if product_spec.warehouse_affinity == warehouse_spec.city.lower():
            base *= 1.3
        elif product_spec.warehouse_affinity == "all":
            base *= 1.0
        elif product_spec.warehouse_affinity == warehouse_spec.city.lower()[:4]:
            base *= 1.2
        else:
            base *= 0.7
        
        month = current_date.month
        if product_spec.seasonality == "summer" and month in [3, 4, 5, 6]:
            base *= 1.6
        elif product_spec.seasonality == "winter" and month in [11, 12, 1, 2]:
            base *= 1.5
        elif product_spec.seasonality == "school_season" and month in [6, 7]:
            base *= 2.5
        
        if current_date.weekday() >= 5:
            base *= self.config.weekend_boost
        
        if day_num >= 30 and day_num <= 60:
            if product_spec.price_tier == "value":
                base *= 1.15
        
        if product_spec.price_tier == "premium" and current_date.day in [5, 10, 15, 20, 25]:
            base *= 0.85
        elif product_spec.price_tier == "value" and current_date.weekday() == 0:
            base *= 1.12
        
        promo_key = (product_spec.sku, warehouse_spec.name)
        if promo_key in self.active_promotions:
            promo_boost = self.active_promotions[promo_key]
            base *= promo_boost
        
        if supplier_disrupted and product_spec.supplier_id == 1 and warehouse_spec.city == "Bangalore":
            base *= 0.2
        
        product_volatility = product_spec.demand_volatility
        noise = self.rng.gauss(1.0, product_volatility)
        demand = int(base * noise)
        
        return max(0, demand)
    
    def activate_promotion(self, sku: str, warehouse_name: str, boost_factor: float, duration_days: int):
        key = (sku, warehouse_name)
        self.active_promotions[key] = boost_factor
    
    def clear_spot_promotions(self):
        pass
    
    def deactivate_promotions(self):
        self.active_promotions.clear()
