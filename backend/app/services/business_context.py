from datetime import date


def fetch_business_context(intent: str, user_input: str, user_id: int) -> dict:
    """Stub for Member 3 analytics APIs; replace internals with HTTP calls when ready."""
    return {
        "as_of": date.today().isoformat(),
        "intent": intent,
        "user_id": user_id,
        "source": "mock_business_context",
        "metrics": {
            "inventory_at_risk_units": 1840,
            "stockout_skus": 7,
            "weekly_revenue": 1284500,
            "margin_delta_pct": -2.4,
            "aging_inventory_value": 214000,
        },
        "signals": [
            "North region has elevated stockout risk on high-velocity personal care SKUs.",
            "Aging inventory is concentrated in seasonal apparel and small electronics.",
            "Revenue is healthy overall, but margin compression suggests discounting pressure.",
        ],
        "member3_handoff": {
            "planned_endpoint": "/analytics/context",
            "query": user_input,
        },
    }
