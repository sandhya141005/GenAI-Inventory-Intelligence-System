from datetime import date

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.analytics_service import AnalyticsService


def fetch_business_context(intent: str, user_input: str, user_id: int, db: Session | None = None, scope=None) -> dict:
    if db is None:
        db = next(get_db())
    
    analytics = AnalyticsService(db, scope)
    user_input_lower = user_input.lower()
    
    context = {
        "as_of": date.today().isoformat(),
        "intent": intent,
        "user_id": user_id,
        "source": "analytics_service",
        "query": user_input,
        "analytics_used": [],
    }
    if scope is not None:
        context["realm_id"] = scope.realm_id
        context["role"] = scope.role
        context["assigned_store_id"] = scope.assigned_store_id

    if scope is not None and getattr(scope, "requires_store_assignment", False):
        context["requires_store_assignment"] = True
        context["message"] = "The user is waiting for a Warehouse Owner to assign a store."
        return context
    
    try:
        if intent == "nl_query":
            from app.models.analytics_data import Product
            
            valid_categories = []
            if scope and scope.realm_id:
                valid_categories = db.query(Product.category).filter(
                    Product.realm_id == scope.realm_id,
                    Product.category.isnot(None)
                ).distinct().order_by(Product.category).all()
                valid_categories = [cat[0] for cat in valid_categories if cat[0]]
            
            context["schema_info"] = {
                "realm_id": scope.realm_id if scope else None,
                "assigned_store_id": scope.assigned_store_id if scope and scope.is_store_manager else None,
                "role": scope.role if scope else None,
                "valid_categories": valid_categories,
                "tables": [
                    "products (product_id, realm_id, sku, name, category, cost, price, expiry_date)",
                    "stores (store_id, realm_id, name, city, region, store_type)",
                    "sales (sale_id, realm_id, product_id, store_id, sale_date, quantity, revenue)",
                    "inventory_stock (product_id, store_id, realm_id, quantity, last_updated)",
                    "transfers (transfer_id, realm_id, from_store, to_store, product_id, quantity, transfer_cost, transfer_date)",
                    "donations_log (id, realm_id, product_id, orphanage_name, orphanage_city, status, created_at)"
                ],
                "access_note": "Store Managers can only query data for their assigned store. Warehouse Owners can query all stores in their realm."
            }
            context["analytics_used"].append("schema_info")
        
        if intent in ("executive_summary", "chat", "morning_brief", "weekly_report"):
            context["overview"] = analytics.overview()
            context["analytics_used"].append("overview")
        
        if intent == "morning_brief":
            context["notices"] = analytics.notices()
            context["inventory"] = analytics.inventory()
            context["analytics_used"].extend(["notices", "inventory"])
        
        if intent == "weekly_report":
            context["charts"] = analytics.charts()
            context["reports"] = analytics.reports()
            context["transfers"] = analytics.transfers()
            context["inventory_aging"] = analytics.inventory_aging()
            context["analytics_used"].extend(["charts", "reports", "transfers", "inventory_aging"])
        
        if intent == "recommendations" or "recommend" in user_input_lower or "action" in user_input_lower:
            context["recommendations"] = analytics.recommendations()
            context["overview"] = analytics.overview()
            context["analytics_used"].extend(["recommendations", "overview"])
        
        if "transfer" in user_input_lower:
            context["transfers"] = analytics.transfers()
            context["analytics_used"].append("transfers")
        
        if "aging" in user_input_lower or "age" in user_input_lower or "old" in user_input_lower:
            context["inventory_aging"] = analytics.inventory_aging()
            context["analytics_used"].append("inventory_aging")
        
        if "warehouse" in user_input_lower or "store" in user_input_lower:
            context["charts"] = analytics.charts()
            context["inventory"] = analytics.inventory()
            context["analytics_used"].extend(["charts", "inventory"])
        
        if "stockout" in user_input_lower or "stock out" in user_input_lower:
            context["inventory"] = analytics.inventory()
            context["notices"] = analytics.notices()
            context["analytics_used"].extend(["inventory", "notices"])
        
        if "overstock" in user_input_lower:
            context["inventory"] = analytics.inventory()
            context["analytics_used"].append("inventory")
        
        if "revenue" in user_input_lower or "sales" in user_input_lower:
            context["charts"] = analytics.charts()
            context["overview"] = analytics.overview()
            context["analytics_used"].extend(["charts", "overview"])
        
        if not context["analytics_used"]:
            context["overview"] = analytics.overview()
            context["inventory"] = analytics.inventory()
            context["analytics_used"].extend(["overview", "inventory"])
        
        context["analytics_used"] = list(set(context["analytics_used"]))
        
    except Exception as e:
        context["error"] = str(e)
        context["partial_failure"] = True
    
    return context
