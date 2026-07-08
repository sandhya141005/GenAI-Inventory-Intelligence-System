from dataclasses import dataclass
from datetime import date


@dataclass
class SimulationConfig:
    simulation_days: int = 360
    random_seed: int = 42
    start_date: date = None
    
    num_warehouses: int = 5
    num_products: int = 56
    
    supplier_disruption_day: int = 90
    disruption_duration: int = 25
    
    summer_promotion_day: int = 45
    clearance_campaign_day: int = 140
    donation_campaign_day: int = 150
    
    base_demand_volatility: float = 0.15
    weekend_boost: float = 1.25
    
    def __post_init__(self):
        if self.start_date is None:
            self.start_date = date.today()
