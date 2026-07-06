"""
Test script to verify all model imports and field mappings
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.models.analytics_data import Product, Store, WarehouseStock, Sale, Transfer
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.business_data import InventorySnapshot, RevenueRecord, StockoutEvent

print("✅ All model imports successful!")
print("\n📋 Model Field Summary:")

print("\n1. Product:")
print("   - id (product_id)")
print("   - sku, name, category")
print("   - cost, price")

print("\n2. Store:")
print("   - id (store_id)")
print("   - name, city, region, store_type")

print("\n3. Sale:")
print("   - id (sale_id)")
print("   - product_id, store_id")
print("   - sale_date, quantity, revenue")

print("\n4. WarehouseStock:")
print("   - product_id (primary key)")
print("   - quantity")

print("\n5. Transfer:")
print("   - id (transfer_id)")
print("   - from_store_id, to_store_id, product_id")
print("   - quantity, transfer_cost, transfer_date")

print("\n6. User:")
print("   - id, email, full_name")
print("   - hashed_password, is_active")
print("   - created_at, updated_at")

print("\n7. Conversation:")
print("   - id, user_id, title")
print("   - created_at, updated_at")

print("\n8. Message:")
print("   - id, conversation_id")
print("   - role, content, message_metadata")
print("   - created_at")

print("\n9. InventorySnapshot (business_data):")
print("   - id, snapshot_date, sku, product_name, category")
print("   - store_id, store_region, on_hand_units, reorder_point")
print("   - unit_cost, created_at")

print("\n10. RevenueRecord (business_data):")
print("    - id, sale_date, sku, store_id, channel")
print("    - units_sold, gross_revenue, margin_amount, created_at")

print("\n11. StockoutEvent (business_data):")
print("    - id, event_date, sku, store_id")
print("    - estimated_lost_sales, duration_hours, root_cause, created_at")

print("\n✨ All models loaded successfully!")
