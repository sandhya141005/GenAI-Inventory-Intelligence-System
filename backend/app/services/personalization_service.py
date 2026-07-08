"""
Personalization Service
Manages personalized report ordering, KPI emphasis, and content prioritization.
"""
from typing import Any

from sqlalchemy.orm import Session

from app.services.persistent_memory import PersistentMemoryService


class PersonalizationService:
    def __init__(self, db: Session, user_id: int, scope=None):
        self.db = db
        self.user_id = user_id
        self.scope = scope
        self.memory_service = PersistentMemoryService(db, user_id, scope)
    
    def personalize_overview(self, overview: dict) -> dict:
        """Personalize overview based on user preferences and history."""
        memory = self.memory_service.build_complete_memory()
        preferences = memory.get("preferences", {})
        
        personalized = overview.copy()
        
        kpis = personalized.get("kpis", [])
        personalized["kpis"] = self._reorder_kpis(kpis, preferences, memory)
        
        recommendations = personalized.get("recommendations", [])
        personalized["recommendations"] = self._prioritize_recommendations(recommendations, memory)
        
        actions = personalized.get("actionSuggestions", [])
        personalized["actionSuggestions"] = self._filter_actions(actions, memory)
        
        return personalized
    
    def personalize_morning_brief(self, context: dict) -> dict:
        """Personalize morning brief based on user role and preferences."""
        memory = self.memory_service.build_complete_memory()
        preferences = memory.get("preferences", {})
        
        personalized = context.copy()
        
        personalized["priority_order"] = self._get_morning_priority_order(memory)
        personalized["emphasis"] = self._get_content_emphasis(memory)
        personalized["greeting"] = self._get_personalized_greeting(memory)
        
        return personalized
    
    def get_personalized_kpi_order(self) -> list[str]:
        """Get personalized KPI ordering based on user role and history."""
        memory = self.memory_service.build_complete_memory()
        role_context = memory.get("business_memory", {}).get("role_context", {})
        preferences = memory.get("preferences", {})
        conversation_memory = memory.get("conversation_memory", {})
        
        topics = conversation_memory.get("topics_discussed", [])
        
        kpi_priorities = []
        
        if "stockout_concerns" in topics:
            kpi_priorities.extend(["stockout-risk", "revenue-at-risk", "days-of-coverage"])
        
        if "overstock_issues" in topics:
            kpi_priorities.extend(["holding-cost", "inventory-turnover"])
        
        if "revenue_analysis" in topics:
            kpi_priorities.extend(["revenue-at-risk", "inventory-turnover", "store-health"])
        
        if role_context.get("responsibility_level") == "strategic":
            kpi_priorities.extend(["store-health", "inventory-turnover", "revenue-at-risk"])
        else:
            kpi_priorities.extend(["stockout-risk", "days-of-coverage", "revenue-at-risk"])
        
        seen = set()
        ordered = []
        for kpi in kpi_priorities:
            if kpi not in seen:
                ordered.append(kpi)
                seen.add(kpi)
        
        default_order = [
            "revenue-at-risk", "stockout-risk", "days-of-coverage",
            "holding-cost", "store-health", "inventory-turnover"
        ]
        
        for kpi in default_order:
            if kpi not in seen:
                ordered.append(kpi)
        
        return ordered
    
    def _reorder_kpis(self, kpis: list[dict], preferences: dict, memory: dict) -> list[dict]:
        """Reorder KPIs based on user preferences."""
        if not kpis:
            return kpis
        
        preferred_order = self.get_personalized_kpi_order()
        
        kpi_map = {kpi["id"]: kpi for kpi in kpis}
        
        reordered = []
        for kpi_id in preferred_order:
            if kpi_id in kpi_map:
                reordered.append(kpi_map[kpi_id])
        
        for kpi in kpis:
            if kpi not in reordered:
                reordered.append(kpi)
        
        return reordered
    
    def _prioritize_recommendations(self, recommendations: list[dict], memory: dict) -> list[dict]:
        """Prioritize recommendations based on user context."""
        if not recommendations:
            return recommendations
        
        conversation_memory = memory.get("conversation_memory", {})
        topics = conversation_memory.get("topics_discussed", [])
        role_context = memory.get("business_memory", {}).get("role_context", {})
        
        scored_recs = []
        for rec in recommendations:
            score = 0
            title = rec.get("title", "").lower()
            reason = rec.get("reason", "").lower()
            priority = rec.get("priority", "medium")
            
            if priority == "critical":
                score += 100
            elif priority == "high":
                score += 50
            elif priority == "medium":
                score += 25
            
            if "stockout_concerns" in topics and any(word in title for word in ["stockout", "expedite", "shortage"]):
                score += 30
            
            if "overstock_issues" in topics and any(word in title for word in ["overstock", "excess", "reduce"]):
                score += 30
            
            if "inventory_transfers" in topics and "transfer" in title:
                score += 25
            
            if role_context.get("responsibility_level") == "strategic":
                if any(word in title for word in ["transfer", "rebalance", "network"]):
                    score += 20
            else:
                if any(word in title for word in ["reorder", "stock", "monitor"]):
                    score += 20
            
            scored_recs.append((score, rec))
        
        scored_recs.sort(key=lambda x: x[0], reverse=True)
        
        return [rec for score, rec in scored_recs]
    
    def _filter_actions(self, actions: list[dict], memory: dict) -> list[dict]:
        """Filter and order actions based on user authority."""
        if not actions:
            return actions
        
        role_context = memory.get("business_memory", {}).get("role_context", {})
        authorities = role_context.get("decision_authority", [])
        
        filtered = []
        for action in actions:
            action_type = action.get("action", "").lower()
            category = action.get("category", "").lower()
            
            if not authorities:
                filtered.append(action)
                continue
            
            if "transfers" in authorities and "transfer" in action_type:
                filtered.append(action)
            elif "reorder_requests" in authorities and "reorder" in action_type:
                filtered.append(action)
            elif "purchasing" in authorities and "purchase" in action_type:
                filtered.append(action)
            else:
                filtered.append(action)
        
        return filtered[:12]
    
    def _get_morning_priority_order(self, memory: dict) -> list[str]:
        """Get priority order for morning brief sections."""
        role_context = memory.get("business_memory", {}).get("role_context", {})
        conversation_memory = memory.get("conversation_memory", {})
        topics = conversation_memory.get("topics_discussed", [])
        
        priority_order = []
        
        if "stockout_concerns" in topics:
            priority_order.append("critical_stockouts")
        
        if role_context.get("responsibility_level") == "strategic":
            priority_order.extend([
                "network_health",
                "store_comparison",
                "critical_stockouts",
                "transfer_opportunities",
                "revenue_highlights"
            ])
        else:
            priority_order.extend([
                "critical_stockouts",
                "todays_priorities",
                "incoming_transfers",
                "revenue_status"
            ])
        
        return priority_order
    
    def _get_content_emphasis(self, memory: dict) -> dict[str, str]:
        """Get content emphasis preferences."""
        preferences = memory.get("preferences", {})
        role_context = memory.get("business_memory", {}).get("role_context", {})
        
        emphasis = {
            "detail_level": "detailed" if preferences.get("prefers_detailed") else "concise",
            "focus": "strategic" if role_context.get("responsibility_level") == "strategic" else "operational",
            "data_presentation": "analytical" if preferences.get("communication_style") == "analytical" else "summary",
        }
        
        return emphasis
    
    def _get_personalized_greeting(self, memory: dict) -> str:
        """Generate personalized greeting."""
        profile = memory.get("user_profile", {})
        name = profile.get("name", "User")
        role = profile.get("role_display", "")
        
        first_name = name.split()[0] if name else "there"
        
        greeting = f"Good morning, {first_name}"
        
        if role:
            greeting += f" ({role})"
        
        location = profile.get("assigned_location")
        if location:
            greeting += f" - {location['name']}"
        
        return greeting
    
    def get_personalized_report_structure(self, report_type: str) -> dict[str, Any]:
        """Get personalized report structure based on user preferences."""
        memory = self.memory_service.build_complete_memory()
        role_context = memory.get("business_memory", {}).get("role_context", {})
        preferences = memory.get("preferences", {})
        
        structure = {
            "report_type": report_type,
            "sections": [],
            "emphasis": self._get_content_emphasis(memory),
            "kpi_order": self.get_personalized_kpi_order(),
        }
        
        if report_type == "morning_brief":
            structure["sections"] = self._get_morning_priority_order(memory)
        
        elif report_type == "weekly_report":
            if role_context.get("responsibility_level") == "strategic":
                structure["sections"] = [
                    "executive_summary",
                    "network_performance",
                    "store_comparisons",
                    "strategic_wins",
                    "challenges",
                    "next_week_priorities"
                ]
            else:
                structure["sections"] = [
                    "store_summary",
                    "weekly_achievements",
                    "inventory_status",
                    "challenges_faced",
                    "next_week_checklist"
                ]
        
        elif report_type == "executive_summary":
            structure["sections"] = [
                "key_metrics",
                "critical_issues",
                "opportunities",
                "recommended_actions"
            ]
        
        return structure
    
    def enhance_context_with_memory(self, context: dict) -> dict:
        """Enhance business context with persistent memory."""
        memory = self.memory_service.build_complete_memory()
        
        enhanced = context.copy()
        enhanced["persistent_memory"] = memory
        enhanced["personalization"] = {
            "kpi_order": self.get_personalized_kpi_order(),
            "greeting": self._get_personalized_greeting(memory),
            "emphasis": self._get_content_emphasis(memory),
        }
        
        return enhanced
