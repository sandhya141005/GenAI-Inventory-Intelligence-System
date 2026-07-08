"""
Persistent Memory Service
Extracts and manages persistent user and organizational memory from existing database.
"""
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func, select, desc
from sqlalchemy.orm import Session

from app.models.analytics_data import Store
from app.models.conversation import Conversation, Message
from app.models.user import User, Realm


class PersistentMemoryService:
    def __init__(self, db: Session, user_id: int, scope=None):
        self.db = db
        self.user_id = user_id
        self.scope = scope
        self.user = db.get(User, user_id)
    
    def build_complete_memory(self) -> dict[str, Any]:
        """Build comprehensive persistent memory from all available sources."""
        return {
            "user_profile": self.get_user_profile(),
            "realm_profile": self.get_realm_profile(),
            "decision_history": self.get_decision_history(),
            "conversation_memory": self.get_conversation_memory(),
            "preferences": self.extract_user_preferences(),
            "business_memory": self.get_business_memory(),
        }
    
    def get_user_profile(self) -> dict[str, Any]:
        """Extract persistent user profile."""
        if not self.user:
            return {}
        
        store = None
        if self.user.assigned_store_id:
            store = self.db.get(Store, self.user.assigned_store_id)
        
        profile = {
            "user_id": self.user.id,
            "name": self.user.full_name or "User",
            "email": self.user.email,
            "role": self.user.role,
            "role_display": self._get_role_display(self.user.role),
            "member_since": self.user.created_at.isoformat() if self.user.created_at else None,
        }
        
        if store:
            profile["assigned_location"] = {
                "store_id": store.id,
                "name": store.name,
                "city": store.city,
                "region": store.region,
                "type": store.store_type,
            }
            profile["primary_region"] = store.region
            profile["primary_city"] = store.city
        
        return profile
    
    def get_realm_profile(self) -> dict[str, Any]:
        """Extract organizational/realm profile."""
        if not self.user or not self.user.realm_id:
            return {}
        
        realm = self.db.get(Realm, self.user.realm_id)
        if not realm:
            return {}
        
        team_count = self.db.execute(
            select(func.count(User.id)).where(User.realm_id == realm.id, User.is_active == True)
        ).scalar() or 0
        
        store_count = self.db.execute(
            select(func.count(Store.id)).where(Store.realm_id == realm.id)
        ).scalar() or 0
        
        stores = self.db.execute(
            select(Store.name, Store.city, Store.region, Store.store_type)
            .where(Store.realm_id == realm.id)
            .order_by(Store.name)
        ).all()
        
        regions = list(set(s.region for s in stores if s.region))
        cities = list(set(s.city for s in stores if s.city))
        
        profile = {
            "realm_id": realm.id,
            "organization_name": realm.name,
            "industry": realm.industry_tag,
            "established": realm.created_at.isoformat() if realm.created_at else None,
            "team_size": team_count,
            "network_size": store_count,
            "operating_regions": sorted(regions),
            "operating_cities": sorted(cities),
            "locations": [
                {
                    "name": s.name,
                    "city": s.city,
                    "region": s.region,
                    "type": s.store_type,
                }
                for s in stores
            ],
        }
        
        return profile
    
    def get_decision_history(self, days: int = 90) -> dict[str, Any]:
        """Extract decision history from conversation metadata."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        messages = self.db.execute(
            select(Message)
            .join(Conversation)
            .where(
                Conversation.user_id == self.user_id,
                Message.role == "assistant",
                Message.created_at >= cutoff,
                Message.message_metadata.isnot(None)
            )
            .order_by(Message.created_at.desc())
            .limit(100)
        ).scalars().all()
        
        recommendations_given = []
        actions_suggested = []
        intents_used = {}
        
        for msg in messages:
            metadata = msg.message_metadata or {}
            intent = metadata.get("intent")
            
            if intent:
                intents_used[intent] = intents_used.get(intent, 0) + 1
            
            if intent == "recommendations":
                recommendations_given.append({
                    "date": msg.created_at.isoformat(),
                    "content_preview": msg.content[:200],
                    "confidence": metadata.get("confidence"),
                })
            
            if "action" in msg.content.lower() or "recommend" in msg.content.lower():
                actions_suggested.append({
                    "date": msg.created_at.isoformat(),
                    "preview": msg.content[:150],
                })
        
        return {
            "period_days": days,
            "total_interactions": len(messages),
            "recommendations_count": len(recommendations_given),
            "recent_recommendations": recommendations_given[:10],
            "actions_suggested": actions_suggested[:10],
            "intent_frequency": intents_used,
            "most_used_feature": max(intents_used.items(), key=lambda x: x[1])[0] if intents_used else None,
        }
    
    def get_conversation_memory(self, days: int = 30) -> dict[str, Any]:
        """Extract cross-conversation memory."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        conversations = self.db.execute(
            select(Conversation)
            .where(
                Conversation.user_id == self.user_id,
                Conversation.updated_at >= cutoff
            )
            .order_by(Conversation.updated_at.desc())
            .limit(20)
        ).scalars().all()
        
        topics_discussed = set()
        products_mentioned = set()
        stores_mentioned = set()
        concerns_raised = []
        
        for conv in conversations:
            messages = self.db.execute(
                select(Message.content, Message.role, Message.created_at)
                .where(Message.conversation_id == conv.id)
                .order_by(Message.id)
            ).all()
            
            for content, role, created_at in messages:
                content_lower = content.lower()
                
                if role == "user":
                    if any(word in content_lower for word in ["stockout", "shortage", "running low"]):
                        topics_discussed.add("stockout_concerns")
                    if any(word in content_lower for word in ["overstock", "excess", "too much"]):
                        topics_discussed.add("overstock_issues")
                    if any(word in content_lower for word in ["transfer", "move", "rebalance"]):
                        topics_discussed.add("inventory_transfers")
                    if any(word in content_lower for word in ["revenue", "sales", "profit"]):
                        topics_discussed.add("revenue_analysis")
                    if any(word in content_lower for word in ["aging", "old", "expiry", "expire"]):
                        topics_discussed.add("aging_inventory")
                    
                    if "urgent" in content_lower or "critical" in content_lower or "emergency" in content_lower:
                        concerns_raised.append({
                            "date": created_at.isoformat(),
                            "concern": content[:100],
                        })
        
        recent_messages = self.db.execute(
            select(Message.content, Message.role, Message.created_at)
            .join(Conversation)
            .where(Conversation.user_id == self.user_id)
            .order_by(Message.created_at.desc())
            .limit(20)
        ).all()
        
        return {
            "period_days": days,
            "conversation_count": len(conversations),
            "topics_discussed": list(topics_discussed),
            "recent_concerns": concerns_raised[-5:],
            "last_interaction": recent_messages[0][2].isoformat() if recent_messages else None,
            "recent_context": [
                {
                    "role": role,
                    "preview": content[:100],
                    "date": created_at.isoformat()
                }
                for content, role, created_at in recent_messages[:10]
            ],
        }
    
    def extract_user_preferences(self) -> dict[str, Any]:
        """Extract user preferences from conversation patterns."""
        messages = self.db.execute(
            select(Message.content, Message.role, Message.message_metadata)
            .join(Conversation)
            .where(Conversation.user_id == self.user_id)
            .order_by(Message.created_at.desc())
            .limit(100)
        ).all()
        
        intent_counts = {}
        confidence_preferences = {"high": 0, "medium": 0, "low": 0}
        question_patterns = {
            "data_focused": 0,
            "action_focused": 0,
            "analytical": 0,
            "quick_summary": 0,
        }
        
        for content, role, metadata in messages:
            if metadata and isinstance(metadata, dict):
                intent = metadata.get("intent")
                if intent:
                    intent_counts[intent] = intent_counts.get(intent, 0) + 1
                
                confidence = metadata.get("confidence", "medium")
                confidence_preferences[confidence] = confidence_preferences.get(confidence, 0) + 1
            
            if role == "user":
                content_lower = content.lower()
                if any(word in content_lower for word in ["show", "list", "what is", "how many"]):
                    question_patterns["data_focused"] += 1
                if any(word in content_lower for word in ["should i", "recommend", "what to do", "action"]):
                    question_patterns["action_focused"] += 1
                if any(word in content_lower for word in ["why", "analyze", "explain", "reason"]):
                    question_patterns["analytical"] += 1
                if len(content) < 50:
                    question_patterns["quick_summary"] += 1
        
        preferred_intent = max(intent_counts.items(), key=lambda x: x[1])[0] if intent_counts else None
        communication_style = max(question_patterns.items(), key=lambda x: x[1])[0] if sum(question_patterns.values()) > 0 else "balanced"
        
        return {
            "preferred_features": intent_counts,
            "top_feature": preferred_intent,
            "communication_style": communication_style,
            "interaction_patterns": question_patterns,
            "prefers_detailed": confidence_preferences.get("high", 0) > confidence_preferences.get("low", 0),
        }
    
    def get_business_memory(self) -> dict[str, Any]:
        """Extract business-specific memory relevant to user's role."""
        memory = {
            "role_context": self._get_role_specific_memory(),
        }
        
        if self.user and self.user.realm_id:
            memory["realm_policies"] = self._extract_realm_policies()
        
        return memory
    
    def _get_role_specific_memory(self) -> dict[str, Any]:
        """Get role-specific business memory."""
        if not self.user or not self.user.role:
            return {}
        
        from app.models.user import WAREHOUSE_OWNER, STORE_MANAGER
        
        if self.user.role == WAREHOUSE_OWNER:
            return {
                "responsibility_level": "strategic",
                "data_access": "full_network",
                "decision_authority": ["transfers", "purchasing", "network_optimization"],
                "key_focus_areas": ["network_performance", "cross_store_efficiency", "strategic_planning"],
            }
        elif self.user.role == STORE_MANAGER:
            return {
                "responsibility_level": "operational",
                "data_access": "single_store",
                "decision_authority": ["reorder_requests", "local_monitoring", "transfer_requests"],
                "key_focus_areas": ["store_operations", "local_inventory", "daily_execution"],
            }
        
        return {}
    
    def _extract_realm_policies(self) -> dict[str, Any]:
        """Extract organizational policies from realm and industry."""
        if not self.user or not self.user.realm_id:
            return {}
        
        realm = self.db.get(Realm, self.user.realm_id)
        if not realm:
            return {}
        
        industry_policies = self._get_industry_policies(realm.industry_tag)
        
        return {
            "industry": realm.industry_tag,
            "industry_priorities": industry_policies.get("priorities", []),
            "compliance_focus": industry_policies.get("compliance", []),
            "terminology": industry_policies.get("terminology", {}),
        }
    
    def _get_industry_policies(self, industry: str) -> dict[str, Any]:
        """Get industry-specific policies and priorities."""
        food_industries = [
            "Food & Beverage", "Groceries", "FMCG", "Packaged Foods",
            "Frozen Foods", "Organic Foods", "Specialty Foods",
        ]
        
        pharma_industries = [
            "Pharmaceuticals", "Pharmacy Retail", "Medical Devices", "Health & Wellness"
        ]
        
        if industry in food_industries:
            return {
                "priorities": ["shelf_life_management", "FIFO_compliance", "freshness", "cold_chain"],
                "compliance": ["food_safety", "expiry_tracking", "temperature_control"],
                "terminology": {
                    "expiry": "shelf life and use-by dates",
                    "storage": "refrigerated, frozen, ambient storage",
                    "rotation": "FIFO (First In, First Out)",
                },
            }
        
        if industry in pharma_industries:
            return {
                "priorities": ["regulatory_compliance", "batch_tracking", "expiry_monitoring", "patient_safety"],
                "compliance": ["pharmaceutical_regulations", "batch_traceability", "controlled_substances"],
                "terminology": {
                    "expiry": "expiration dates and beyond-use dates",
                    "storage": "controlled temperature storage",
                    "rotation": "batch and lot management",
                },
            }
        
        return {
            "priorities": ["inventory_optimization", "cost_management", "demand_fulfillment"],
            "compliance": ["standard_operations"],
            "terminology": {},
        }
    
    def _get_role_display(self, role: str | None) -> str:
        """Get display name for role."""
        from app.models.user import WAREHOUSE_OWNER, STORE_MANAGER
        
        if role == WAREHOUSE_OWNER:
            return "Warehouse Owner"
        elif role == STORE_MANAGER:
            return "Store Manager"
        return "User"
    
    def format_memory_for_llm(self, memory: dict[str, Any]) -> str:
        """Format persistent memory as structured text for LLM context."""
        sections = []
        
        sections.append("=== PERSISTENT USER PROFILE ===")
        profile = memory.get("user_profile", {})
        if profile:
            sections.append(f"Name: {profile.get('name')}")
            sections.append(f"Role: {profile.get('role_display')}")
            if profile.get("assigned_location"):
                loc = profile["assigned_location"]
                sections.append(f"Location: {loc['name']} ({loc['city']}, {loc['region']})")
            sections.append(f"Member Since: {profile.get('member_since', 'N/A')[:10]}")
        
        sections.append("\n=== ORGANIZATION CONTEXT ===")
        realm = memory.get("realm_profile", {})
        if realm:
            sections.append(f"Organization: {realm.get('organization_name')}")
            sections.append(f"Industry: {realm.get('industry')}")
            sections.append(f"Network: {realm.get('network_size')} locations across {len(realm.get('operating_regions', []))} regions")
            if realm.get("operating_regions"):
                sections.append(f"Regions: {', '.join(realm['operating_regions'][:5])}")
        
        sections.append("\n=== DECISION HISTORY (Last 90 Days) ===")
        history = memory.get("decision_history", {})
        if history:
            sections.append(f"Total Interactions: {history.get('total_interactions', 0)}")
            sections.append(f"Recommendations Given: {history.get('recommendations_count', 0)}")
            if history.get("most_used_feature"):
                sections.append(f"Most Used Feature: {history['most_used_feature']}")
            
            if history.get("recent_recommendations"):
                sections.append("\nRecent Recommendations:")
                for rec in history["recent_recommendations"][:3]:
                    sections.append(f"  • {rec.get('date', '')[:10]}: {rec.get('content_preview', '')[:80]}...")
        
        sections.append("\n=== CONVERSATION MEMORY (Last 30 Days) ===")
        conv_mem = memory.get("conversation_memory", {})
        if conv_mem:
            sections.append(f"Recent Conversations: {conv_mem.get('conversation_count', 0)}")
            if conv_mem.get("topics_discussed"):
                topics = ", ".join(conv_mem["topics_discussed"])
                sections.append(f"Topics Discussed: {topics}")
            
            if conv_mem.get("recent_concerns"):
                sections.append("\nRecent Concerns:")
                for concern in conv_mem["recent_concerns"]:
                    sections.append(f"  • {concern.get('date', '')[:10]}: {concern.get('concern', '')}")
        
        sections.append("\n=== USER PREFERENCES ===")
        prefs = memory.get("preferences", {})
        if prefs:
            sections.append(f"Communication Style: {prefs.get('communication_style', 'balanced')}")
            if prefs.get("top_feature"):
                sections.append(f"Preferred Feature: {prefs['top_feature']}")
            sections.append(f"Detail Level: {'Detailed' if prefs.get('prefers_detailed') else 'Concise'}")
        
        sections.append("\n=== BUSINESS MEMORY ===")
        biz_mem = memory.get("business_memory", {})
        if biz_mem.get("role_context"):
            role_ctx = biz_mem["role_context"]
            sections.append(f"Responsibility: {role_ctx.get('responsibility_level', 'operational')}")
            sections.append(f"Data Access: {role_ctx.get('data_access', 'limited')}")
            if role_ctx.get("key_focus_areas"):
                sections.append(f"Focus Areas: {', '.join(role_ctx['key_focus_areas'])}")
        
        if biz_mem.get("realm_policies"):
            policies = biz_mem["realm_policies"]
            if policies.get("industry_priorities"):
                sections.append(f"Industry Priorities: {', '.join(policies['industry_priorities'][:3])}")
        
        sections.append("\n" + "=" * 60)
        
        return "\n".join(sections)
