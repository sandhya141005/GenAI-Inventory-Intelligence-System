import random
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional


@dataclass
class ProductSpec:
    sku: str
    name: str
    category: str
    price: Decimal
    cost: Decimal
    expiry_days: Optional[int]
    base_demand: int
    seasonality: str
    supplier_id: int
    warehouse_affinity: str
    demand_volatility: float
    price_tier: str


@dataclass
class WarehouseSpec:
    name: str
    city: str
    region: str
    store_type: str
    personality: str
    demand_multiplier: float
    replenishment_aggressiveness: float
    category_preferences: dict


@dataclass
class SupplierSpec:
    supplier_id: int
    name: str
    lead_time_days: int
    reliability: float
    cities_served: List[str]
    will_fail: bool
    failure_start_day: int
    failure_duration: int


class CompanyGenerator:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
    
    def generate_warehouses(self) -> List[WarehouseSpec]:
        return [
            WarehouseSpec(
                "Chennai Flagship", "Chennai", "South", "hub", "healthy_hub", 1.0, 0.9,
                {"Grains": 1.15, "Pulses": 1.10, "Oils": 1.05, "Spices": 1.20, "Sweeteners": 1.05, "Dry Fruits": 1.40, "Pickles": 1.10, "Fresh Produce": 1.08, "Dairy": 1.12, "Ready to Eat": 0.95}
            ),
            WarehouseSpec(
                "Bangalore Metro", "Bangalore", "South", "store", "high_demand", 1.4, 0.7,
                {"Grains": 1.30, "Pulses": 1.20, "Oils": 1.15, "Spices": 1.25, "Sweeteners": 1.05, "Dry Fruits": 1.50, "Pickles": 1.15, "Fresh Produce": 1.35, "Dairy": 1.45, "Ready to Eat": 1.60}
            ),
            WarehouseSpec(
                "Hyderabad Central", "Hyderabad", "South", "store", "overstock", 0.7, 1.5,
                {"Grains": 0.90, "Pulses": 1.00, "Oils": 0.85, "Spices": 1.30, "Sweeteners": 0.95, "Dry Fruits": 0.75, "Pickles": 1.45, "Fresh Produce": 0.80, "Dairy": 0.85, "Ready to Eat": 0.70}
            ),
            WarehouseSpec(
                "Coimbatore Regional", "Coimbatore", "South", "store", "stable", 0.85, 1.0,
                {"Grains": 1.05, "Pulses": 1.10, "Oils": 0.95, "Spices": 1.15, "Sweeteners": 1.10, "Dry Fruits": 0.90, "Pickles": 1.00, "Fresh Produce": 0.92, "Dairy": 1.00, "Ready to Eat": 0.85}
            ),
            WarehouseSpec(
                "Kochi Fresh Market", "Kochi", "South", "store", "food_heavy", 0.9, 0.95,
                {"Grains": 1.25, "Pulses": 1.35, "Oils": 1.40, "Spices": 1.50, "Sweeteners": 1.15, "Dry Fruits": 1.10, "Pickles": 1.35, "Fresh Produce": 1.60, "Dairy": 1.30, "Ready to Eat": 1.00}
            ),
        ]
    
    def generate_suppliers(self, disruption_day: int, disruption_duration: int) -> List[SupplierSpec]:
        return [
            SupplierSpec(1, "Southern Foods Distribution", 5, 0.95, ["Chennai", "Bangalore", "Kochi"], True, disruption_day, disruption_duration),
            SupplierSpec(2, "Metro Beverages Ltd", 4, 0.98, ["Bangalore", "Hyderabad"], False, 0, 0),
            SupplierSpec(3, "Care Products India", 7, 0.92, ["Chennai", "Hyderabad", "Coimbatore"], False, 0, 0),
            SupplierSpec(4, "National Stationers", 10, 0.88, ["Bangalore", "Coimbatore"], False, 0, 0),
            SupplierSpec(5, "Baby World Distributors", 6, 0.95, ["Chennai", "Bangalore", "Kochi"], False, 0, 0),
        ]
    
    def generate_products(self) -> List[ProductSpec]:
        products = [
            # Rice & Grains (15 products)
            ProductSpec("RICE-BAS-5KG", "Basmati Rice 5kg Premium", "Grains", Decimal("485"), Decimal("340"), 180, 42, "stable", 1, "all", 0.18, "premium"),
            ProductSpec("RICE-WHT-1KG", "White Rice 1kg", "Grains", Decimal("65"), Decimal("42"), 180, 95, "stable", 1, "all", 0.12, "value"),
            ProductSpec("RICE-BRN-1KG", "Brown Rice 1kg Organic", "Grains", Decimal("125"), Decimal("85"), 180, 28, "stable", 1, "chennai", 0.25, "premium"),
            ProductSpec("RICE-SNA-500G", "Sona Masoori Rice 500g", "Grains", Decimal("38"), Decimal("25"), 180, 68, "stable", 1, "hyderabad", 0.16, "value"),
            ProductSpec("RICE-IDL-1KG", "Idli Rice 1kg", "Grains", Decimal("55"), Decimal("38"), 180, 52, "stable", 1, "kochi", 0.18, "value"),
            ProductSpec("RICE-PON-500G", "Ponni Rice 500g", "Grains", Decimal("42"), Decimal("28"), 180, 58, "stable", 1, "all", 0.14, "value"),
            ProductSpec("WHEAT-WHL-1KG", "Whole Wheat 1kg", "Grains", Decimal("48"), Decimal("32"), 120, 75, "stable", 1, "all", 0.12, "value"),
            ProductSpec("FLOUR-APF-1KG", "All Purpose Flour 1kg", "Grains", Decimal("52"), Decimal("35"), 90, 82, "stable", 1, "all", 0.14, "value"),
            ProductSpec("FLOUR-WHT-5KG", "Wheat Flour 5kg", "Grains", Decimal("240"), Decimal("175"), 120, 56, "stable", 1, "bangalore", 0.16, "standard"),
            ProductSpec("FLOUR-RIC-500G", "Rice Flour 500g", "Grains", Decimal("38"), Decimal("25"), 90, 45, "stable", 1, "kochi", 0.20, "value"),
            ProductSpec("FLOUR-BES-500G", "Besan Flour 500g", "Grains", Decimal("65"), Decimal("45"), 120, 38, "stable", 1, "all", 0.18, "standard"),
            ProductSpec("FLOUR-RAG-500G", "Ragi Flour 500g Organic", "Grains", Decimal("85"), Decimal("58"), 90, 22, "stable", 1, "chennai", 0.28, "premium"),
            ProductSpec("SEMOL-RAV-500G", "Rava Semolina 500g", "Grains", Decimal("45"), Decimal("30"), 120, 48, "stable", 1, "all", 0.16, "value"),
            ProductSpec("OATS-ROL-1KG", "Rolled Oats 1kg", "Grains", Decimal("165"), Decimal("115"), 180, 35, "stable", 1, "bangalore", 0.22, "standard"),
            ProductSpec("POHA-THK-500G", "Thick Poha 500g", "Grains", Decimal("42"), Decimal("28"), 60, 42, "stable", 1, "all", 0.18, "value"),
            
            # Pulses & Lentils (15 products)
            ProductSpec("DAL-TUR-1KG", "Toor Dal 1kg", "Pulses", Decimal("145"), Decimal("105"), 365, 52, "stable", 1, "all", 0.15, "standard"),
            ProductSpec("DAL-MNG-1KG", "Moong Dal 1kg", "Pulses", Decimal("155"), Decimal("110"), 365, 45, "stable", 1, "all", 0.16, "standard"),
            ProductSpec("DAL-URA-1KG", "Urad Dal 1kg", "Pulses", Decimal("165"), Decimal("118"), 365, 38, "stable", 1, "kochi", 0.18, "standard"),
            ProductSpec("DAL-CHN-1KG", "Chana Dal 1kg", "Pulses", Decimal("135"), Decimal("95"), 365, 42, "stable", 1, "all", 0.16, "standard"),
            ProductSpec("DAL-MAS-1KG", "Masoor Dal 1kg", "Pulses", Decimal("125"), Decimal("88"), 365, 48, "stable", 1, "all", 0.14, "standard"),
            ProductSpec("CHANA-WHT-1KG", "White Chickpeas 1kg", "Pulses", Decimal("95"), Decimal("68"), 365, 55, "stable", 1, "all", 0.12, "value"),
            ProductSpec("CHANA-BLK-1KG", "Black Chickpeas 1kg", "Pulses", Decimal("105"), Decimal("75"), 365, 32, "stable", 1, "hyderabad", 0.20, "standard"),
            ProductSpec("RAJMA-RED-1KG", "Red Kidney Beans 1kg", "Pulses", Decimal("145"), Decimal("105"), 365, 28, "stable", 1, "bangalore", 0.22, "standard"),
            ProductSpec("BEANS-BLK-500G", "Black Beans 500g", "Pulses", Decimal("85"), Decimal("60"), 365, 18, "stable", 1, "chennai", 0.28, "standard"),
            ProductSpec("PEAS-GRN-500G", "Green Peas Dried 500g", "Pulses", Decimal("75"), Decimal("52"), 365, 25, "stable", 1, "all", 0.24, "value"),
            ProductSpec("LENTIL-RED-500G", "Red Lentils 500g", "Pulses", Decimal("85"), Decimal("60"), 365, 35, "stable", 1, "all", 0.18, "standard"),
            ProductSpec("LENTIL-GRN-500G", "Green Lentils 500g", "Pulses", Decimal("95"), Decimal("68"), 365, 28, "stable", 1, "coimbatore", 0.22, "standard"),
            ProductSpec("SOYB-CHK-200G", "Soya Chunks 200g", "Pulses", Decimal("55"), Decimal("38"), 180, 38, "stable", 1, "all", 0.20, "value"),
            ProductSpec("SOYB-GRN-200G", "Soya Granules 200g", "Pulses", Decimal("48"), Decimal("32"), 180, 32, "stable", 1, "bangalore", 0.22, "value"),
            ProductSpec("MOONG-SPR-250G", "Moong Sprouts Mix 250g", "Pulses", Decimal("45"), Decimal("30"), 5, 22, "stable", 1, "kochi", 0.35, "standard"),
            
            # Cooking Oils (10 products)
            ProductSpec("OIL-SUN-1L", "Sunflower Oil 1L", "Oils", Decimal("165"), Decimal("120"), 90, 72, "stable", 1, "bangalore", 0.16, "standard"),
            ProductSpec("OIL-SUN-5L", "Sunflower Oil 5L", "Oils", Decimal("795"), Decimal("580"), 90, 25, "stable", 1, "all", 0.18, "standard"),
            ProductSpec("OIL-GND-1L", "Groundnut Oil 1L", "Oils", Decimal("185"), Decimal("135"), 90, 48, "stable", 1, "all", 0.18, "standard"),
            ProductSpec("OIL-SES-500ML", "Sesame Oil 500ml", "Oils", Decimal("195"), Decimal("140"), 120, 32, "stable", 1, "chennai", 0.22, "standard"),
            ProductSpec("OIL-MUS-500ML", "Mustard Oil 500ml", "Oils", Decimal("125"), Decimal("90"), 90, 38, "stable", 1, "hyderabad", 0.20, "standard"),
            ProductSpec("OIL-COC-500ML", "Coconut Oil 500ml", "Oils", Decimal("165"), Decimal("120"), 120, 55, "stable", 1, "kochi", 0.18, "standard"),
            ProductSpec("OIL-OLV-500ML", "Olive Oil 500ml Premium", "Oils", Decimal("520"), Decimal("380"), 60, 12, "stable", 1, "chennai", 0.32, "premium"),
            ProductSpec("OIL-RIC-1L", "Rice Bran Oil 1L", "Oils", Decimal("175"), Decimal("125"), 90, 28, "stable", 1, "bangalore", 0.24, "standard"),
            ProductSpec("OIL-SOY-1L", "Soybean Oil 1L", "Oils", Decimal("155"), Decimal("112"), 90, 42, "stable", 1, "all", 0.16, "standard"),
            ProductSpec("GHEE-PUR-500ML", "Pure Cow Ghee 500ml", "Oils", Decimal("385"), Decimal("275"), 180, 35, "stable", 1, "all", 0.20, "premium"),
            
            # Spices & Masalas (20 products)
            ProductSpec("SPICE-TUR-100G", "Turmeric Powder 100g", "Spices", Decimal("45"), Decimal("30"), 365, 65, "stable", 2, "all", 0.14, "value"),
            ProductSpec("SPICE-CHI-100G", "Red Chilli Powder 100g", "Spices", Decimal("55"), Decimal("38"), 365, 72, "stable", 2, "all", 0.16, "value"),
            ProductSpec("SPICE-COR-100G", "Coriander Powder 100g", "Spices", Decimal("48"), Decimal("32"), 365, 58, "stable", 2, "all", 0.14, "value"),
            ProductSpec("SPICE-CUM-100G", "Cumin Powder 100g", "Spices", Decimal("65"), Decimal("45"), 365, 48, "stable", 2, "all", 0.18, "standard"),
            ProductSpec("SPICE-GAR-50G", "Garam Masala 50g", "Spices", Decimal("55"), Decimal("38"), 365, 52, "stable", 2, "all", 0.16, "standard"),
            ProductSpec("SPICE-SAM-100G", "Sambar Powder 100g", "Spices", Decimal("65"), Decimal("45"), 365, 45, "stable", 2, "kochi", 0.18, "standard"),
            ProductSpec("SPICE-BIR-50G", "Biryani Masala 50g", "Spices", Decimal("75"), Decimal("52"), 365, 42, "stable", 2, "hyderabad", 0.20, "standard"),
            ProductSpec("SPICE-TEA-100G", "Tea Masala 100g", "Spices", Decimal("85"), Decimal("60"), 365, 35, "stable", 2, "all", 0.22, "standard"),
            ProductSpec("SPICE-CHT-100G", "Chaat Masala 100g", "Spices", Decimal("68"), Decimal("48"), 365, 32, "stable", 2, "bangalore", 0.24, "standard"),
            ProductSpec("SPICE-TND-50G", "Tandoori Masala 50g", "Spices", Decimal("72"), Decimal("50"), 365, 28, "stable", 2, "all", 0.22, "standard"),
            ProductSpec("MUSTARD-SED-100G", "Mustard Seeds 100g", "Spices", Decimal("42"), Decimal("28"), 365, 55, "stable", 2, "all", 0.14, "value"),
            ProductSpec("CUMIN-SED-100G", "Cumin Seeds 100g", "Spices", Decimal("85"), Decimal("60"), 365, 45, "stable", 2, "all", 0.18, "standard"),
            ProductSpec("FENUGRK-50G", "Fenugreek Seeds 50g", "Spices", Decimal("35"), Decimal("24"), 365, 38, "stable", 2, "all", 0.20, "value"),
            ProductSpec("CARDM-GRN-25G", "Green Cardamom 25g", "Spices", Decimal("185"), Decimal("135"), 365, 18, "stable", 2, "chennai", 0.28, "premium"),
            ProductSpec("CLOVE-WHT-25G", "Cloves 25g", "Spices", Decimal("125"), Decimal("90"), 365, 22, "stable", 2, "all", 0.24, "standard"),
            ProductSpec("CINNAMON-50G", "Cinnamon Sticks 50g", "Spices", Decimal("95"), Decimal("68"), 365, 28, "stable", 2, "kochi", 0.22, "standard"),
            ProductSpec("PEPPER-BLK-100G", "Black Pepper 100g", "Spices", Decimal("145"), Decimal("105"), 365, 32, "stable", 2, "all", 0.20, "standard"),
            ProductSpec("BAY-LEAF-25G", "Bay Leaves 25g", "Spices", Decimal("48"), Decimal("32"), 365, 25, "stable", 2, "all", 0.24, "value"),
            ProductSpec("NUTMEG-WHT-25G", "Nutmeg Whole 25g", "Spices", Decimal("95"), Decimal("68"), 365, 15, "stable", 2, "chennai", 0.30, "standard"),
            ProductSpec("ASAFOET-50G", "Asafoetida Powder 50g", "Spices", Decimal("125"), Decimal("90"), 365, 22, "stable", 2, "all", 0.26, "standard"),
            
            # Sugar, Salt & Sweeteners (8 products)
            ProductSpec("SUGAR-WHT-1KG", "White Sugar 1kg", "Sweeteners", Decimal("48"), Decimal("34"), 730, 85, "stable", 1, "all", 0.10, "value"),
            ProductSpec("SUGAR-BRN-1KG", "Brown Sugar 1kg", "Sweeteners", Decimal("75"), Decimal("52"), 730, 28, "stable", 1, "bangalore", 0.22, "standard"),
            ProductSpec("JAGGERY-PUR-500G", "Pure Jaggery 500g", "Sweeteners", Decimal("85"), Decimal("60"), 180, 42, "stable", 1, "all", 0.18, "standard"),
            ProductSpec("JAGGERY-POW-500G", "Jaggery Powder 500g", "Sweeteners", Decimal("95"), Decimal("68"), 180, 32, "stable", 1, "kochi", 0.20, "standard"),
            ProductSpec("HONEY-PUR-500G", "Pure Honey 500g", "Sweeteners", Decimal("285"), Decimal("205"), 730, 22, "stable", 1, "all", 0.24, "premium"),
            ProductSpec("SALT-IOD-1KG", "Iodized Salt 1kg", "Sweeteners", Decimal("22"), Decimal("15"), 1095, 95, "stable", 1, "all", 0.08, "value"),
            ProductSpec("SALT-ROK-500G", "Rock Salt 500g", "Sweeteners", Decimal("45"), Decimal("30"), 1095, 28, "stable", 1, "all", 0.18, "value"),
            ProductSpec("SALT-BLK-250G", "Black Salt 250g", "Sweeteners", Decimal("38"), Decimal("25"), 1095, 25, "stable", 1, "hyderabad", 0.20, "value"),
            
            # Dry Fruits & Nuts (12 products)
            ProductSpec("ALMOND-RAW-250G", "Raw Almonds 250g", "Dry Fruits", Decimal("385"), Decimal("280"), 365, 28, "stable", 3, "all", 0.22, "premium"),
            ProductSpec("CASHEW-WHT-250G", "Whole Cashews 250g", "Dry Fruits", Decimal("420"), Decimal("310"), 365, 25, "stable", 3, "chennai", 0.24, "premium"),
            ProductSpec("WALNUT-KER-200G", "Walnut Kernels 200g", "Dry Fruits", Decimal("485"), Decimal("360"), 365, 18, "stable", 3, "bangalore", 0.28, "premium"),
            ProductSpec("PISTACHIO-200G", "Pistachios 200g", "Dry Fruits", Decimal("625"), Decimal("470"), 365, 12, "stable", 3, "chennai", 0.35, "premium"),
            ProductSpec("RAISIN-BLK-250G", "Black Raisins 250g", "Dry Fruits", Decimal("145"), Decimal("105"), 365, 38, "stable", 3, "all", 0.18, "standard"),
            ProductSpec("RAISIN-GRN-250G", "Green Raisins 250g", "Dry Fruits", Decimal("165"), Decimal("120"), 365, 32, "stable", 3, "all", 0.20, "standard"),
            ProductSpec("DATE-DRY-250G", "Dried Dates 250g", "Dry Fruits", Decimal("185"), Decimal("135"), 180, 35, "stable", 3, "all", 0.22, "standard"),
            ProductSpec("FIG-DRY-200G", "Dried Figs 200g", "Dry Fruits", Decimal("285"), Decimal("210"), 180, 22, "stable", 3, "bangalore", 0.26, "premium"),
            ProductSpec("APRICOT-DRY-200G", "Dried Apricots 200g", "Dry Fruits", Decimal("245"), Decimal("180"), 180, 18, "stable", 3, "chennai", 0.28, "premium"),
            ProductSpec("PEANUT-RAW-500G", "Raw Peanuts 500g", "Dry Fruits", Decimal("95"), Decimal("68"), 180, 48, "stable", 3, "all", 0.16, "value"),
            ProductSpec("COCONUT-DRY-200G", "Dry Coconut 200g", "Dry Fruits", Decimal("95"), Decimal("68"), 120, 42, "stable", 3, "kochi", 0.18, "standard"),
            ProductSpec("MIX-DRYFRUT-250G", "Mixed Dry Fruits 250g", "Dry Fruits", Decimal("385"), Decimal("280"), 180, 28, "stable", 3, "all", 0.24, "premium"),
            
            # Pickles & Chutneys (8 products)
            ProductSpec("PICKLE-MNG-500G", "Mango Pickle 500g", "Pickles", Decimal("125"), Decimal("90"), 180, 52, "stable", 2, "all", 0.18, "standard"),
            ProductSpec("PICKLE-LMN-500G", "Lemon Pickle 500g", "Pickles", Decimal("105"), Decimal("75"), 180, 45, "stable", 2, "all", 0.16, "standard"),
            ProductSpec("PICKLE-MIX-500G", "Mixed Pickle 500g", "Pickles", Decimal("115"), Decimal("82"), 180, 48, "stable", 2, "all", 0.18, "standard"),
            ProductSpec("PICKLE-GAR-250G", "Garlic Pickle 250g", "Pickles", Decimal("95"), Decimal("68"), 180, 35, "stable", 2, "hyderabad", 0.22, "standard"),
            ProductSpec("CHUTN-COC-200G", "Coconut Chutney Powder 200g", "Pickles", Decimal("75"), Decimal("52"), 90, 42, "stable", 2, "kochi", 0.20, "standard"),
            ProductSpec("CHUTN-TOM-200G", "Tomato Chutney Powder 200g", "Pickles", Decimal("68"), Decimal("48"), 90, 38, "stable", 2, "all", 0.18, "standard"),
            ProductSpec("CHUTN-MINT-200G", "Mint Chutney Powder 200g", "Pickles", Decimal("85"), Decimal("60"), 90, 28, "stable", 2, "bangalore", 0.24, "standard"),
            ProductSpec("PAPAD-URA-200G", "Urad Papad 200g", "Pickles", Decimal("55"), Decimal("38"), 120, 58, "stable", 2, "all", 0.16, "value"),
            
            # Frozen & Fresh Produce (10 products)
            ProductSpec("VEG-POT-1KG", "Fresh Potatoes 1kg", "Fresh Produce", Decimal("35"), Decimal("22"), 14, 125, "stable", 1, "all", 0.18, "value"),
            ProductSpec("VEG-ONI-1KG", "Fresh Onions 1kg", "Fresh Produce", Decimal("45"), Decimal("28"), 21, 135, "stable", 1, "all", 0.22, "value"),
            ProductSpec("VEG-TOM-1KG", "Fresh Tomatoes 1kg", "Fresh Produce", Decimal("48"), Decimal("30"), 7, 115, "stable", 1, "all", 0.25, "value"),
            ProductSpec("VEG-CAR-500G", "Fresh Carrots 500g", "Fresh Produce", Decimal("32"), Decimal("20"), 14, 68, "stable", 1, "all", 0.20, "value"),
            ProductSpec("VEG-BEA-500G", "Fresh Beans 500g", "Fresh Produce", Decimal("55"), Decimal("35"), 5, 52, "stable", 1, "kochi", 0.28, "value"),
            ProductSpec("VEG-CAB-1PC", "Fresh Cabbage 1pc", "Fresh Produce", Decimal("28"), Decimal("18"), 10, 75, "stable", 1, "all", 0.22, "value"),
            ProductSpec("VEG-CAU-1PC", "Fresh Cauliflower 1pc", "Fresh Produce", Decimal("42"), Decimal("26"), 7, 58, "stable", 1, "all", 0.24, "value"),
            ProductSpec("PEAS-FRZ-500G", "Frozen Green Peas 500g", "Fresh Produce", Decimal("85"), Decimal("60"), 180, 62, "stable", 1, "all", 0.16, "standard"),
            ProductSpec("CORN-FRZ-400G", "Frozen Sweet Corn 400g", "Fresh Produce", Decimal("95"), Decimal("68"), 180, 48, "stable", 1, "bangalore", 0.18, "standard"),
            ProductSpec("MIXED-VEG-500G", "Frozen Mixed Vegetables 500g", "Fresh Produce", Decimal("105"), Decimal("75"), 180, 55, "stable", 1, "all", 0.16, "standard"),
            
            # Dairy Products (10 products)
            ProductSpec("MILK-FUL-1L", "Full Cream Milk 1L", "Dairy", Decimal("62"), Decimal("42"), 5, 145, "stable", 2, "all", 0.14, "value"),
            ProductSpec("MILK-TON-1L", "Toned Milk 1L", "Dairy", Decimal("52"), Decimal("36"), 5, 125, "stable", 2, "all", 0.12, "value"),
            ProductSpec("CURD-FRE-500G", "Fresh Curd 500g", "Dairy", Decimal("48"), Decimal("32"), 3, 95, "stable", 2, "all", 0.18, "value"),
            ProductSpec("PANEER-FRE-200G", "Fresh Paneer 200g", "Dairy", Decimal("95"), Decimal("68"), 5, 68, "stable", 2, "all", 0.20, "standard"),
            ProductSpec("BUTTER-UNS-200G", "Unsalted Butter 200g", "Dairy", Decimal("125"), Decimal("90"), 60, 52, "stable", 2, "all", 0.16, "standard"),
            ProductSpec("BUTTER-SAL-200G", "Salted Butter 200g", "Dairy", Decimal("125"), Decimal("90"), 60, 48, "stable", 2, "all", 0.16, "standard"),
            ProductSpec("CHEESE-CHE-200G", "Cheddar Cheese 200g", "Dairy", Decimal("185"), Decimal("135"), 90, 38, "stable", 2, "bangalore", 0.22, "standard"),
            ProductSpec("CHEESE-MOZ-200G", "Mozzarella Cheese 200g", "Dairy", Decimal("195"), Decimal("142"), 90, 35, "stable", 2, "bangalore", 0.24, "standard"),
            ProductSpec("CREAM-FRE-200ML", "Fresh Cream 200ml", "Dairy", Decimal("85"), Decimal("60"), 14, 42, "stable", 2, "all", 0.20, "standard"),
            ProductSpec("YOGURT-GRK-200G", "Greek Yogurt 200g", "Dairy", Decimal("125"), Decimal("90"), 21, 32, "stable", 2, "chennai", 0.24, "premium"),
            
            # Ready to Cook/Eat (12 products)
            ProductSpec("RTE-POH-200G", "Instant Poha Mix 200g", "Ready to Eat", Decimal("55"), Decimal("38"), 180, 42, "stable", 1, "all", 0.18, "value"),
            ProductSpec("RTE-UPM-200G", "Instant Upma Mix 200g", "Ready to Eat", Decimal("52"), Decimal("36"), 180, 38, "stable", 1, "all", 0.16, "value"),
            ProductSpec("RTE-IDL-200G", "Instant Idli Mix 200g", "Ready to Eat", Decimal("68"), Decimal("48"), 180, 48, "stable", 1, "kochi", 0.18, "standard"),
            ProductSpec("RTE-DOS-500G", "Instant Dosa Mix 500g", "Ready to Eat", Decimal("95"), Decimal("68"), 180, 52, "stable", 1, "all", 0.16, "standard"),
            ProductSpec("RTE-PAN-200G", "Pancake Mix 200g", "Ready to Eat", Decimal("85"), Decimal("60"), 180, 32, "stable", 1, "bangalore", 0.22, "standard"),
            ProductSpec("RTE-PAST-500G", "Pasta Penne 500g", "Ready to Eat", Decimal("95"), Decimal("68"), 365, 58, "stable", 4, "all", 0.16, "standard"),
            ProductSpec("RTE-MACA-500G", "Macaroni 500g", "Ready to Eat", Decimal("85"), Decimal("60"), 365, 52, "stable", 4, "bangalore", 0.18, "standard"),
            ProductSpec("RTE-NOOD-500G", "Instant Noodles 500g", "Ready to Eat", Decimal("75"), Decimal("52"), 180, 85, "stable", 4, "all", 0.14, "value"),
            ProductSpec("RTE-SOOP-200G", "Instant Soup Mix 200g", "Ready to Eat", Decimal("105"), Decimal("75"), 365, 35, "stable", 4, "bangalore", 0.20, "standard"),
            ProductSpec("RTE-CORN-200G", "Cornflakes 200g", "Ready to Eat", Decimal("95"), Decimal("68"), 180, 62, "stable", 4, "all", 0.16, "standard"),
            ProductSpec("RTE-MUES-500G", "Muesli Mix 500g", "Ready to Eat", Decimal("285"), Decimal("205"), 180, 28, "stable", 4, "bangalore", 0.24, "premium"),
            ProductSpec("RTE-SOUP-KUB", "Soup Cubes Variety Pack", "Ready to Eat", Decimal("125"), Decimal("90"), 365, 32, "stable", 4, "all", 0.22, "standard"),]
        return products
    
    def generate_orphanages(self) -> List[dict]:
        return [
            {"name": "Sunrise Children's Home", "city": "Chennai", "email": "sunrise.home@example.org"},
            {"name": "Hope Bridge Foundation", "city": "Bangalore", "email": "hope.bridge@example.org"},
            {"name": "New Dawn Home", "city": "Hyderabad", "email": "newdawn.home@example.org"},
            {"name": "Little Stars Home", "city": "Kochi", "email": "littlestars.home@example.org"},
            {"name": "Asha Nivas Care", "city": "Coimbatore", "email": "ashanivas.care@example.org"},
        ]
