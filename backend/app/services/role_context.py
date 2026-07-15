"""
Role Context Service
Builds role-specific context for personalized LLM interactions.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.analytics_data import Store
from app.models.user import STORE_MANAGER, WAREHOUSE_OWNER, Realm


def build_role_context(scope, db: Session) -> dict:
    """
    Build comprehensive role context for LLM personalization.
    
    Returns:
        dict with role_name, data_scope, permissions, and location info
    """
    if scope is None:
        return {
            "role_name": "User",
            "data_scope": "Limited access",
            "can_view_all_stores": False,
            "can_initiate_transfers": False,
        }
    
    context = {
        "role": scope.role,
        "role_name": _get_role_display_name(scope.role),
        "can_view_all_stores": scope.is_owner,
        "can_initiate_transfers": scope.is_owner,
    }
    
    if scope.is_store_manager:
        return _build_store_manager_context(context, scope, db)
    elif scope.is_owner:
        return _build_warehouse_owner_context(context, scope, db)
    
    return context


def _build_store_manager_context(context: dict, scope, db: Session) -> dict:
    """Build context specific to store managers."""
    context.update({
        "data_scope": "Single Store",
        "perspective": "operational",
        "focus": "day-to-day store operations",
    })
    
    if scope.assigned_store_id:
        store = db.get(Store, scope.assigned_store_id)
        if store:
            context["assigned_store"] = {
                "id": store.id,
                "name": store.name,
                "city": store.city or "Unknown",
                "region": store.region or "Unknown",
                "type": store.store_type or "Store",
            }
            context["data_scope_description"] = (
                f"You can only see data for {store.name} in {store.city}. "
                f"You cannot view inventory or sales from other locations."
            )
            context["transfer_permissions"] = (
                f"You can request transfers TO {store.name} from the warehouse, "
                f"but cannot view inventory levels at other stores."
            )
        else:
            context["data_scope_description"] = "Awaiting store assignment from Warehouse Owner"
            context["transfer_permissions"] = "No transfer permissions until store assignment"
    else:
        context["requires_assignment"] = True
        context["data_scope_description"] = "Awaiting store assignment from Warehouse Owner"
    
    return context


def _build_warehouse_owner_context(context: dict, scope, db: Session) -> dict:
    """Build context specific to warehouse owners."""
    # Count stores in realm
    store_count = db.execute(
        select(func.count(Store.id)).where(Store.realm_id == scope.realm_id)
    ).scalar() or 0
    
    # Get store list
    stores = db.execute(
        select(Store.name, Store.city)
        .where(Store.realm_id == scope.realm_id)
        .order_by(Store.name)
    ).all()
    
    store_locations = [f"{name} ({city})" for name, city in stores] if stores else []
    
    context.update({
        "data_scope": "Full Network",
        "perspective": "strategic",
        "focus": "network optimization and multi-location management",
        "network_size": store_count,
        "network_locations": store_locations[:10],  # Limit to avoid token bloat
        "data_scope_description": (
            f"You have full visibility across {store_count} location{'s' if store_count != 1 else ''} "
            f"in your network. You can view and compare all stores, initiate transfers, "
            f"and optimize inventory distribution."
        ),
        "transfer_permissions": (
            "You can initiate transfers between any stores in your network and "
            "have visibility into inventory levels at all locations."
        ),
    })
    
    return context


def build_industry_context(industry_tag: str | None) -> dict:
    """
    Build industry-specific context for terminology and focus areas.
    
    Returns:
        dict with industry name, terminology, and focus areas
    """
    if not industry_tag:
        return {
            "industry": "Retail",
            "product_term": "products",
            "expiry_focus": False,
            "terminology": {},
        }
    
    industry_map = {
        # Food & Perishables
        ("Food & Beverage", "Groceries", "FMCG", "Packaged Foods", "Frozen Foods", 
         "Organic Foods", "Specialty Foods", "Bakery", "Dairy", "Meat & Seafood"): {
            "industry": industry_tag,
            "product_term": "food products and groceries",
            "expiry_focus": True,
            "expiry_terminology": "shelf life, use-by dates, FIFO rotation, cold chain",
            "storage_terminology": "refrigerated, frozen, ambient, cold storage",
            "focus_areas": ["expiry management", "FIFO compliance", "cold chain integrity", "freshness"],
            "urgency_factors": ["approaching expiry dates", "temperature control"],
        },
        
        # Pharmaceuticals
        ("Pharmaceuticals", "Pharmacy Retail", "Medical Devices", "Health & Wellness"): {
            "industry": industry_tag,
            "product_term": "pharmaceutical products and medicines",
            "expiry_focus": True,
            "expiry_terminology": "expiration dates, beyond-use dates, batch numbers, stability",
            "storage_terminology": "controlled temperature, refrigerated, room temperature",
            "focus_areas": ["regulatory compliance", "expiry monitoring", "batch tracking", "controlled substances"],
            "urgency_factors": ["critical medicines", "regulatory deadlines", "patient safety"],
        },
        
        # Electronics
        ("Electronics", "Consumer Electronics", "Mobile Accessories", "Computer Hardware"): {
            "industry": industry_tag,
            "product_term": "electronic products and devices",
            "expiry_focus": False,
            "expiry_terminology": "product lifecycle, technology obsolescence, warranty periods",
            "storage_terminology": "climate controlled, anti-static, secure storage",
            "focus_areas": ["technology obsolescence", "warranty management", "new model cycles"],
            "urgency_factors": ["new product launches", "end-of-life models", "rapid depreciation"],
        },
        
        # Textiles & Apparel
        ("Textile & Apparel", "Footwear", "Fashion", "Leather Goods"): {
            "industry": industry_tag,
            "product_term": "apparel and fashion items",
            "expiry_focus": False,
            "expiry_terminology": "seasonality, fashion cycles, trend cycles",
            "storage_terminology": "climate controlled, organized by season/size",
            "focus_areas": ["seasonal inventory", "size distribution", "style trends"],
            "urgency_factors": ["end of season", "style obsolescence", "size gaps"],
        },
    }
    
    # Find matching industry group
    for industry_group, context in industry_map.items():
        if industry_tag in industry_group:
            return context
    
    # Default for unlisted industries
    return {
        "industry": industry_tag or "Retail",
        "product_term": "products",
        "expiry_focus": False,
        "focus_areas": ["inventory optimization", "demand fulfillment"],
        "urgency_factors": ["stockouts", "overstock"],
    }


def _get_role_display_name(role: str | None) -> str:
    """Get user-friendly role name."""
    if role == WAREHOUSE_OWNER:
        return "Warehouse Owner"
    elif role == STORE_MANAGER:
        return "Store Manager"
    return "User"


def format_role_context_for_llm(role_context: dict, industry_context: dict) -> str:
    """
    Format role and industry context into a clear, concise string for LLM.
    
    Returns:
        Formatted string describing user's role, permissions, and context
    """
    lines = [
        "=== USER CONTEXT ===",
        f"Role: {role_context['role_name']}",
        f"Industry: {industry_context['industry']}",
        f"Data Access: {role_context['data_scope']}",
        "",
    ]
    
    # Add store info for store managers
    if "assigned_store" in role_context:
        store = role_context["assigned_store"]
        lines.extend([
            f"Assigned Store: {store['name']} ({store['city']}, {store['region']})",
            f"Store Type: {store['type']}",
            "",
        ])
    
    # Add network info for warehouse owners
    if "network_size" in role_context:
        lines.extend([
            f"Network Size: {role_context['network_size']} locations",
        ])
        if role_context.get("network_locations"):
            locations_preview = ", ".join(role_context["network_locations"][:5])
            more = len(role_context["network_locations"]) - 5
            if more > 0:
                locations_preview += f" (+{more} more)"
            lines.append(f"Locations: {locations_preview}")
        lines.append("")
    
    # Data scope explanation
    lines.append(f"Data Scope: {role_context['data_scope_description']}")
    
    # Industry-specific focus
    if industry_context.get("focus_areas"):
        focus = ", ".join(industry_context["focus_areas"])
        lines.append(f"Industry Focus: {focus}")
    
    lines.append("=" * 40)
    
    return "\n".join(lines)
