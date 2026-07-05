from datetime import date


def fetch_business_context(intent: str, user_input: str, user_id: int) -> dict:
    return {
        "as_of": date.today().isoformat(),
        "intent": intent,
        "user_id": user_id,
        "source": "analytics_service",
        "metrics": {},
        "signals": [],
        "analytics_endpoints": [
            "/api/analytics/overview",
            "/api/analytics/inventory",
            "/api/analytics/recommendations",
            "/api/analytics/charts",
            "/api/analytics/transfers",
            "/api/analytics/inventory-aging",
            "/api/analytics/notices",
        ],
        "query": user_input,
    }
