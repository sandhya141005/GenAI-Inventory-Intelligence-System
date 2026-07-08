"""
Business Simulation - Procedural Retail Operations
Generates realistic operational history through day-by-day business simulation
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import date, timedelta

from app.db.session import SessionLocal
from app.services.analytics_service import AnalyticsService
from app.services.action_engine import SmartInventoryActionEngine

from simulator.config import SimulationConfig
from simulator.simulation import DailySimulationEngine
from simulator.persistence import DatabasePersistence


def run_business_simulation():
    print("\n" + "="*70)
    print("🚀 STOCKLENS RETAIL - BUSINESS SIMULATION")
    print("="*70)
    
    config = SimulationConfig(
        simulation_days=180,
        random_seed=42,
        start_date=date.today() - timedelta(days=180),
        supplier_disruption_day=90,
        disruption_duration=25,
        summer_promotion_day=45,
        clearance_campaign_day=140,
        donation_campaign_day=150,
    )
    
    db = SessionLocal()
    
    try:
        persistence = DatabasePersistence(db)
        persistence.clear_existing_data()
        
        _, realm_id = persistence.create_realm_and_owner()
        
        simulator = DailySimulationEngine(config)
        simulation_results = simulator.run_simulation()
        
        end_date = config.start_date + timedelta(days=config.simulation_days - 1)
        persistence.persist_simulation_results(simulation_results, realm_id, end_date)
        
        print("\n🔍 Validating simulation results...")
        analytics = AnalyticsService(db, scope=None)
        overview = analytics.overview()
        
        action_engine = SmartInventoryActionEngine(db, scope=None)
        actions = action_engine.suggestions()
        
        action_counts = {
            "CLEARANCE_SALE": len([a for a in actions if a["action"] == "CLEARANCE_SALE"]),
            "DONATE": len([a for a in actions if a["action"] == "DONATE"]),
            "DISCARD": len([a for a in actions if a["action"] == "DISCARD"]),
        }
        
        sales_count = len(simulation_results["inventory_state"].sales_history)
        transfer_count = len(simulation_results["inventory_state"].transfer_history)
        stockout_count = len(simulation_results["inventory_state"].stockout_events)
        
        print(f"   ✓ Dashboard: {len(overview['kpis'])} KPIs")
        print(f"   ✓ Smart Actions: {len(actions)} total")
        print(f"      - Clearance: {action_counts['CLEARANCE_SALE']}")
        print(f"      - Donate: {action_counts['DONATE']}")
        print(f"      - Discard: {action_counts['DISCARD']}")
        print(f"   ✓ Sales transactions: {sales_count:,}")
        print(f"   ✓ Transfers: {transfer_count}")
        print(f"   ✓ Stockout events: {stockout_count}")
        
        print("\n" + "="*70)
        print("✅ SIMULATION COMPLETE")
        print("="*70)
        
        print("\n📊 BUSINESS NARRATIVE:")
        print("   • 180-day operational simulation")
        print("   • Day 45: Summer promotion boost")
        print("   • Day 90-115: Supplier disruption → Bangalore stockouts")
        print("   • Day 105: Emergency transfers from Chennai")
        print("   • Day 120: Demand normalization")
        print("   • Day 140: Clearance campaign")
        print("   • Day 150: Donation campaign")
        print("   • Day 170+: Recovery phase")
        
        print("\n🏪 WAREHOUSE CHARACTERISTICS:")
        print("   • Chennai: Healthy hub, emergency transfer source")
        print("   • Bangalore: High demand, supplier disruption victim")
        print("   • Hyderabad: Over-ordered, overstock situation")
        print("   • Coimbatore: Stable operations, aging inventory")
        print("   • Kochi: Food-heavy, expiry challenges")
        
        print("\n📈 SIMULATION METRICS:")
        print(f"   Products: {len(simulation_results['product_specs'])}")
        print(f"   Warehouses: {len(simulation_results['warehouse_specs'])}")
        print(f"   Suppliers: {len(simulation_results['supplier_specs'])}")
        print(f"   Sales Transactions: {sales_count:,}")
        print(f"   Transfers: {transfer_count}")
        print(f"   Stockout Events: {stockout_count}")
        print(f"   Business Events: {len(simulation_results['events_triggered'])}")
        
        print("\n🔐 LOGIN:")
        print("   Email: ops@stocklens.com")
        print("   Password: stocklens2024")
        print("   Realm: SL24")
        
        print("\n✨ Every metric traces back to simulated business events!")
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
    run_business_simulation()
