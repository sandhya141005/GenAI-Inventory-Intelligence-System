from datetime import date

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.analytics_service import AnalyticsService


def fetch_business_context(intent: str, user_input: str, user_id: int, db: Session | None = None) -> dict:
    if db is None:
        db = next(get_db())
    
    analytics = AnalyticsService(db)
    user_input_lower = user_input.lower()
    
    context = {
        "as_of": date.today().isoformat(),
        "intent": intent,
        "user_id": user_id,
        "source": "analytics_service",
        "query": user_input,
        "analytics_used": [],
    }
    
    try:
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
