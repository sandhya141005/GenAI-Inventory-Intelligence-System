"""
Context Enrichment Service
Provides detailed, role-specific data enrichment for personalized LLM responses.
"""
from typing import Any

from app.services.role_context import build_industry_context


def enrich_business_context(context: dict, role_context: dict, industry_tag: str | None) -> dict:
    """
    Enrich business context with detailed, role-specific insights.
    
    Converts raw analytics data into narrative format tailored to user's role.
    Returns enriched context with detailed summaries, comparisons, and priorities.
    """
    enriched = {
        "role_narrative": _build_role_narrative(role_context),
        "industry_context": build_industry_context(industry_tag),
        "detailed_insights": {},
    }
    
    # Enrich based on available analytics
    if "overview" in context:
        enriched["detailed_insights"]["overview"] = _enrich_overview(
            context["overview"], role_context
        )
    
    if "inventory" in context:
        enriched["detailed_insights"]["inventory"] = _enrich_inventory(
            context["inventory"], role_context
        )
    
    if "recommendations" in context:
        enriched["detailed_insights"]["recommendations"] = _enrich_recommendations(
            context["recommendations"], role_context
        )
    
    if "transfers" in context:
        enriched["detailed_insights"]["transfers"] = _enrich_transfers(
            context["transfers"], role_context
        )
    
    if "charts" in context:
        enriched["detailed_insights"]["charts"] = _enrich_charts(
            context["charts"], role_context
        )
    
    if "notices" in context:
        enriched["detailed_insights"]["notices"] = _enrich_notices(
            context["notices"], role_context
        )
    
    if "inventory_aging" in context:
        enriched["detailed_insights"]["aging"] = _enrich_aging(
            context["inventory_aging"], role_context
        )
    
    return enriched


def _build_role_narrative(role_context: dict) -> str:
    """Build a narrative description of the user's role and context."""
    role_name = role_context.get("role_name", "User")
    data_scope = role_context.get("data_scope_description", "")
    
    narrative = f"User Role: {role_name}\n"
    narrative += f"Data Scope: {data_scope}\n"
    
    if "assigned_store" in role_context:
        store = role_context["assigned_store"]
        narrative += f"Managing: {store['name']} in {store['city']}, {store['region']}\n"
        narrative += "Perspective: Single-location operational management\n"
    elif "network_size" in role_context:
        narrative += f"Managing: {role_context['network_size']} locations across the network\n"
        narrative += "Perspective: Strategic network-wide management\n"
    
    return narrative


def _enrich_overview(overview: dict, role_context: dict) -> dict:
    """Enrich overview with role-specific interpretation."""
    is_store_manager = role_context.get("role") == "STORE_MANAGER"
    
    enriched = {
        "summary_text": overview.get("summary", {}).get("headline", ""),
        "kpi_analysis": [],
        "priority_recommendations": [],
        "urgency_level": "medium",
    }
    
    # Analyze KPIs with role context
    kpis = overview.get("kpis", [])
    critical_kpis = []
    
    for kpi in kpis:
        kpi_analysis = {
            "id": kpi.get("id"),
            "label": kpi.get("label"),
            "value": kpi.get("value"),
            "status": kpi.get("status"),
            "interpretation": _interpret_kpi(kpi, is_store_manager),
        }
        enriched["kpi_analysis"].append(kpi_analysis)
        
        if kpi.get("status") == "risk":
            critical_kpis.append(kpi.get("label"))
    
    # Set urgency based on critical KPIs
    if len(critical_kpis) >= 2:
        enriched["urgency_level"] = "high"
        enriched["critical_areas"] = critical_kpis
    elif len(critical_kpis) == 1:
        enriched["urgency_level"] = "medium"
        enriched["critical_areas"] = critical_kpis
    
    # Get top recommendations with role context
    recommendations = overview.get("recommendations", [])[:5]
    for rec in recommendations:
        priority_text = _format_recommendation_for_role(rec, is_store_manager)
        enriched["priority_recommendations"].append(priority_text)
    
    # Action suggestions
    actions = overview.get("actionSuggestions", [])[:8]
    enriched["smart_actions"] = [
        f"{act.get('category', 'Action')}: {act.get('sku', 'Product')} - {act.get('action', 'Review')}"
        for act in actions
    ]
    
    return enriched


def _interpret_kpi(kpi: dict, is_store_manager: bool) -> str:
    """Interpret KPI value with role-specific context."""
    label = kpi.get("label", "")
    value = kpi.get("value", "")
    status = kpi.get("status", "")
    
    scope = "at your store" if is_store_manager else "across the network"
    
    if "Revenue at Risk" in label:
        if status == "risk":
            return f"High revenue exposure {scope}: {value} needs immediate attention"
        else:
            return f"Revenue risk {scope} is under control: {value}"
    
    elif "Stockout Risk" in label:
        count = value.split()[0] if value else "0"
        if status == "risk":
            return f"Critical: {count} products facing stockout {scope}"
        else:
            return f"Stock levels healthy {scope}: {count} minor risks"
    
    elif "Holding Cost" in label:
        return f"Inventory carrying cost {scope}: {value}"
    
    elif "Health Score" in label:
        score = value.rstrip("%")
        if status == "good":
            return f"Strong operational health {scope}: {value}"
        else:
            return f"Health score needs improvement {scope}: {value}"
    
    elif "Days of Coverage" in label:
        return f"Average inventory runway {scope}: {value}"
    
    elif "Turnover" in label:
        return f"Inventory turnover rate {scope}: {value}"
    
    return f"{label} {scope}: {value}"


def _format_recommendation_for_role(rec: dict, is_store_manager: bool) -> str:
    """Format recommendation with role-appropriate language."""
    title = rec.get("title", "")
    reason = rec.get("reason", "")
    priority = rec.get("priority", "medium")
    
    if is_store_manager:
        # Simplify for store manager - focus on what they can control
        if "Transfer" in title:
            return f"[{priority.upper()}] Request transfer: {reason}"
        elif "Expedite" in title or "Reorder" in title:
            return f"[{priority.upper()}] Stock alert: {reason}"
        else:
            return f"[{priority.upper()}] {title}: {reason}"
    else:
        # Full detail for warehouse owner
        return f"[{priority.upper()}] {title}: {reason}"


def _enrich_inventory(inventory: dict, role_context: dict) -> dict:
    """Enrich inventory data with detailed analysis."""
    items = inventory.get("items", [])
    is_store_manager = role_context.get("role") == "STORE_MANAGER"
    
    enriched = {
        "total_items": len(items),
        "critical_items": [],
        "healthy_items": [],
        "overstock_items": [],
        "categories_affected": set(),
        "summary": "",
    }
    
    for item in items:
        health = item.get("health", "")
        status = item.get("status", "")
        
        if health == "critical" or status == "stockout":
            enriched["critical_items"].append({
                "sku": item.get("sku"),
                "product": item.get("product"),
                "store": item.get("store"),
                "inventory": item.get("inventory"),
                "days": item.get("daysOfCover"),
                "revenue_risk": item.get("revenueAtRisk"),
            })
            enriched["categories_affected"].add(item.get("product", "").split()[0])
        
        elif health == "overstock":
            enriched["overstock_items"].append({
                "sku": item.get("sku"),
                "product": item.get("product"),
                "store": item.get("store"),
                "inventory": item.get("inventory"),
                "days": item.get("daysOfCover"),
            })
        
        elif health == "healthy":
            enriched["healthy_items"].append(item.get("product"))
    
    # Build summary
    critical_count = len(enriched["critical_items"])
    overstock_count = len(enriched["overstock_items"])
    
    scope = "your store" if is_store_manager else "the network"
    
    if critical_count > 0:
        enriched["summary"] = f"{critical_count} critical items at {scope} need immediate action. "
    if overstock_count > 0:
        enriched["summary"] += f"{overstock_count} overstocked items could be rebalanced."
    
    enriched["categories_affected"] = list(enriched["categories_affected"])
    
    # Limit lists for token efficiency
    enriched["critical_items"] = enriched["critical_items"][:10]
    enriched["overstock_items"] = enriched["overstock_items"][:10]
    
    return enriched


def _enrich_recommendations(recommendations: dict, role_context: dict) -> dict:
    """Enrich recommendations with role-specific prioritization."""
    recs = recommendations.get("recommendations", [])
    is_store_manager = role_context.get("role") == "STORE_MANAGER"
    
    enriched = {
        "total_recommendations": len(recs),
        "critical_actions": [],
        "high_priority": [],
        "medium_priority": [],
        "actionable_now": [],
    }
    
    for rec in recs:
        priority = rec.get("priority", "medium")
        confidence = rec.get("confidence", 0)
        
        rec_summary = {
            "title": rec.get("title"),
            "reason": rec.get("reason"),
            "impact": rec.get("impact"),
            "action": rec.get("primaryAction"),
            "savings": rec.get("estimatedSavings"),
            "confidence": confidence,
        }
        
        # Categorize by priority
        if priority == "critical":
            enriched["critical_actions"].append(rec_summary)
        elif priority == "high":
            enriched["high_priority"].append(rec_summary)
        elif priority == "medium":
            enriched["medium_priority"].append(rec_summary)
        
        # Identify immediately actionable items for role
        if is_store_manager:
            # Store managers can act on stockouts, requests, monitoring
            if any(word in rec.get("title", "") for word in ["Reorder", "Stock", "Monitor"]):
                enriched["actionable_now"].append(rec_summary)
        else:
            # Warehouse owners can act on transfers, purchasing, rebalancing
            if any(word in rec.get("title", "") for word in ["Transfer", "Purchase", "Rebalance"]):
                enriched["actionable_now"].append(rec_summary)
    
    # Limit for token efficiency
    enriched["critical_actions"] = enriched["critical_actions"][:5]
    enriched["high_priority"] = enriched["high_priority"][:8]
    enriched["actionable_now"] = enriched["actionable_now"][:6]
    
    return enriched


def _enrich_transfers(transfers: dict, role_context: dict) -> dict:
    """Enrich transfer data with role-specific insights."""
    transfer_list = transfers.get("transfers", [])
    is_store_manager = role_context.get("role") == "STORE_MANAGER"
    assigned_store = role_context.get("assigned_store", {}).get("name") if is_store_manager else None
    
    enriched = {
        "total_transfers": len(transfer_list),
        "completed": [],
        "recommended": [],
        "incoming_to_user": [],
        "outgoing_from_user": [],
    }
    
    for transfer in transfer_list:
        status = transfer.get("status", "")
        from_store = transfer.get("from", "")
        to_store = transfer.get("to", "")
        
        transfer_info = {
            "product": transfer.get("product"),
            "from": from_store,
            "to": to_store,
            "units": transfer.get("units"),
            "status": status,
            "revenue_protected": transfer.get("revenueAtRisk"),
        }
        
        if status == "Completed":
            enriched["completed"].append(transfer_info)
        elif status == "Recommended":
            enriched["recommended"].append(transfer_info)
        
        # For store managers, categorize by relevance
        if is_store_manager and assigned_store:
            if to_store == assigned_store:
                enriched["incoming_to_user"].append(transfer_info)
            elif from_store == assigned_store:
                enriched["outgoing_from_user"].append(transfer_info)
    
    # Limit for token efficiency
    enriched["completed"] = enriched["completed"][:5]
    enriched["recommended"] = enriched["recommended"][:8]
    
    return enriched


def _enrich_charts(charts: dict, role_context: dict) -> dict:
    """Enrich chart data with trend analysis."""
    enriched = {
        "revenue_trend": _analyze_trend(charts.get("revenueTrend", {})),
        "store_performance": _analyze_performance(charts.get("storePerformance", {})),
        "category_distribution": _analyze_categories(charts.get("categoryMix", {})),
    }
    
    return enriched


def _analyze_trend(trend_data: dict) -> dict:
    """Analyze revenue trend for patterns."""
    values = trend_data.get("values", [])
    if not values or len(values) < 2:
        return {"trend": "insufficient_data"}
    
    # Simple trend analysis
    recent_avg = sum(values[-3:]) / 3 if len(values) >= 3 else values[-1]
    older_avg = sum(values[:3]) / 3 if len(values) >= 3 else values[0]
    
    change_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
    
    if change_pct > 5:
        direction = "increasing"
    elif change_pct < -5:
        direction = "decreasing"
    else:
        direction = "stable"
    
    return {
        "trend": direction,
        "change_percent": round(change_pct, 1),
        "recent_average": round(recent_avg, 2),
        "interpretation": f"Revenue trend is {direction} ({change_pct:+.1f}%)",
    }


def _analyze_performance(performance_data: dict) -> dict:
    """Analyze store performance distribution."""
    labels = performance_data.get("labels", [])
    values = performance_data.get("values", [])
    
    if not labels or not values:
        return {"status": "no_data"}
    
    # Pair stores with scores
    stores = list(zip(labels, values))
    stores.sort(key=lambda x: x[1], reverse=True)
    
    return {
        "best_performer": stores[0][0] if stores else None,
        "worst_performer": stores[-1][0] if stores else None,
        "average_score": round(sum(values) / len(values), 1) if values else 0,
        "performance_gap": stores[0][1] - stores[-1][1] if len(stores) > 1 else 0,
    }


def _analyze_categories(category_data: dict) -> dict:
    """Analyze category distribution."""
    labels = category_data.get("labels", [])
    values = category_data.get("values", [])
    
    if not labels or not values:
        return {"status": "no_data"}
    
    categories = list(zip(labels, values))
    categories.sort(key=lambda x: x[1], reverse=True)
    
    total = sum(values)
    
    return {
        "top_category": categories[0][0] if categories else None,
        "top_category_percent": round(categories[0][1] / total * 100, 1) if total > 0 and categories else 0,
        "category_count": len(categories),
        "distribution": "concentrated" if categories and categories[0][1] / total > 0.4 else "balanced",
    }


def _enrich_notices(notices: dict, role_context: dict) -> dict:
    """Enrich notices with urgency and categorization."""
    notice_list = notices.get("notices", [])
    
    enriched = {
        "total_notices": len(notice_list),
        "stockout_alerts": [],
        "recommendations": [],
        "critical_count": 0,
    }
    
    for notice in notice_list:
        category = notice.get("category", "")
        
        notice_info = {
            "title": notice.get("title"),
            "detail": notice.get("detail"),
            "category": category,
        }
        
        if category == "Stockout":
            enriched["stockout_alerts"].append(notice_info)
            enriched["critical_count"] += 1
        elif category == "Recommendation":
            enriched["recommendations"].append(notice_info)
    
    # Limit for token efficiency
    enriched["stockout_alerts"] = enriched["stockout_alerts"][:8]
    enriched["recommendations"] = enriched["recommendations"][:6]
    
    return enriched


def _enrich_aging(aging: dict, role_context: dict) -> dict:
    """Enrich aging inventory data."""
    items = aging.get("items", [])
    
    enriched = {
        "total_aging_items": len(items),
        "high_value_aging": [],
        "total_value_at_risk": 0,
    }
    
    # Sort by value
    sorted_items = sorted(items, key=lambda x: x.get("value", 0), reverse=True)
    
    for item in sorted_items[:10]:
        value = item.get("value", 0)
        enriched["total_value_at_risk"] += value
        
        enriched["high_value_aging"].append({
            "product": item.get("product"),
            "store": item.get("store"),
            "age_days": item.get("ageDays"),
            "value": value,
        })
    
    return enriched


def format_enriched_context_for_llm(enriched: dict) -> str:
    """Format enriched context into structured text for LLM."""
    sections = []
    
    # Role narrative
    if "role_narrative" in enriched:
        sections.append("=== USER ROLE & CONTEXT ===")
        sections.append(enriched["role_narrative"])
    
    # Detailed insights
    insights = enriched.get("detailed_insights", {})
    
    if "overview" in insights:
        sections.append("\n=== OVERVIEW ANALYSIS ===")
        overview = insights["overview"]
        sections.append(f"Urgency: {overview.get('urgency_level', 'medium').upper()}")
        sections.append(f"Summary: {overview.get('summary_text', '')}")
        
        if overview.get("critical_areas"):
            sections.append(f"Critical Areas: {', '.join(overview['critical_areas'])}")
        
        if overview.get("kpi_analysis"):
            sections.append("\nKey Metrics:")
            for kpi in overview["kpi_analysis"][:5]:
                sections.append(f"  • {kpi['interpretation']}")
    
    if "inventory" in insights:
        sections.append("\n=== INVENTORY ANALYSIS ===")
        inv = insights["inventory"]
        sections.append(inv.get("summary", ""))
        
        if inv.get("critical_items"):
            sections.append(f"\nCritical Items ({len(inv['critical_items'])}):")
            for item in inv["critical_items"][:5]:
                sections.append(
                    f"  • {item['product']} at {item['store']}: "
                    f"{item['inventory']} units, {item['days']:.1f} days coverage"
                )
    
    if "recommendations" in insights:
        sections.append("\n=== PRIORITY RECOMMENDATIONS ===")
        recs = insights["recommendations"]
        
        if recs.get("critical_actions"):
            sections.append("CRITICAL:")
            for rec in recs["critical_actions"][:3]:
                sections.append(f"  • {rec['title']}: {rec['reason']}")
        
        if recs.get("actionable_now"):
            sections.append("\nActionable Now:")
            for rec in recs["actionable_now"][:3]:
                sections.append(f"  • {rec['action']}")
    
    if "transfers" in insights:
        sections.append("\n=== TRANSFER STATUS ===")
        trans = insights["transfers"]
        
        if trans.get("incoming_to_user"):
            sections.append("Incoming to Your Store:")
            for t in trans["incoming_to_user"][:3]:
                sections.append(f"  • {t['product']}: {t['units']} units from {t['from']}")
        
        if trans.get("recommended"):
            sections.append(f"\nRecommended Transfers ({len(trans['recommended'])}):")
            for t in trans["recommended"][:3]:
                sections.append(f"  • {t['product']}: {t['from']} → {t['to']} ({t['units']} units)")
    
    sections.append("\n" + "=" * 50)
    
    return "\n".join(sections)
