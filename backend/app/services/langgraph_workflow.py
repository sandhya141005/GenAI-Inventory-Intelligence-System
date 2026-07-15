from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.business_context import fetch_business_context
from app.services.llm_client import LLMClient
from app.services.prompt_service import load_prompt


class CopilotState(TypedDict, total=False):
    user_input: str
    requested_intent: str | None
    intent: str
    user_id: int
    business_context: dict[str, Any]
    conversation_history: list[dict[str, str]]
    metadata: dict[str, Any]
    scope: Any
    llm_response: str
    response: str
    confidence: str
    analytics_used: list[str]
    error: str | None
    db: Session | None


def classify_intent(state: CopilotState) -> CopilotState:
    requested = state.get("requested_intent")
    if requested and requested != "chat":
        state["intent"] = requested
        return state
    
    from app.services.intent_classifier import IntentClassifier
    
    classifier = IntentClassifier()
    conversation_history = state.get("conversation_history", [])
    
    intent = classifier.classify(state["user_input"], conversation_history)
    confidence = classifier.get_intent_confidence(state["user_input"], intent)
    
    state["intent"] = intent
    state["intent_confidence"] = confidence
    
    return state


def add_business_context(state: CopilotState) -> CopilotState:
    try:
        db = state.get("db") or next(get_db())
        scope = state.get("scope")
        
        # Fetch business analytics data
        state["business_context"] = fetch_business_context(
            intent=state["intent"],
            user_input=state["user_input"],
            user_id=state["user_id"],
            db=db,
            scope=scope,
        )
        
        # Add role-specific context enrichment
        if scope:
            from app.services.role_context import build_role_context
            from app.models.user import User
            
            state["business_context"]["role_context"] = build_role_context(scope, db)
            
            # Add industry context
            user = db.get(User, state["user_id"])
            if user and user.realm:
                state["business_context"]["industry_tag"] = user.realm.industry_tag
        
        # Add persistent memory and personalization
        from app.services.persistent_memory import PersistentMemoryService
        from app.services.personalization_service import PersonalizationService
        
        memory_service = PersistentMemoryService(db, state["user_id"], scope)
        personalization_service = PersonalizationService(db, state["user_id"], scope)
        
        persistent_memory = memory_service.build_complete_memory()
        state["business_context"]["persistent_memory"] = persistent_memory
        
        if "overview" in state["business_context"]:
            state["business_context"]["overview"] = personalization_service.personalize_overview(
                state["business_context"]["overview"]
            )
        
        state["business_context"] = personalization_service.enhance_context_with_memory(
            state["business_context"]
        )
        
        state["analytics_used"] = state["business_context"].get("analytics_used", [])
    except Exception as e:
        state["error"] = f"Failed to fetch business context: {str(e)}"
        state["business_context"] = {
            "error": str(e),
            "partial_failure": True,
            "as_of": "",
            "intent": state["intent"],
        }
        state["analytics_used"] = []
    return state


def call_llm(state: CopilotState) -> CopilotState:
    if state.get("error"):
        state["llm_response"] = (
            "I encountered an issue accessing the inventory analytics. "
            "Please try again or contact support if the problem persists."
        )
        state["confidence"] = "low"
        return state
    
    try:
        # Get role and industry for personalized prompt
        scope = state.get("scope")
        role = scope.role if scope else None
        
        context = state['business_context']
        industry_tag = context.get("industry_tag")
        role_ctx = context.get("role_context", {})
        
        # Load role and industry-specific prompt
        prompt = load_prompt(state["intent"], role=role, industry=industry_tag)
        
        # Format conversation history
        history = state.get("conversation_history", [])
        history_text = ""
        if history:
            history_text = "\n**Recent Conversation:**\n"
            for msg in history[-6:]:
                role_label = "You" if msg['role'] == "assistant" else "User"
                history_text += f"{role_label}: {msg['content'][:150]}\n"
            history_text += "\n"
        
        # ENHANCED: Rich context enrichment
        from app.services.context_enrichment import (
            enrich_business_context,
            format_enriched_context_for_llm
        )
        from app.services.persistent_memory import PersistentMemoryService
        
        enriched_context = enrich_business_context(context, role_ctx, industry_tag)
        detailed_context_text = format_enriched_context_for_llm(enriched_context)
        
        # Add persistent memory to context
        persistent_memory = context.get("persistent_memory", {})
        memory_text = ""
        if persistent_memory:
            db = state.get("db")
            if db:
                memory_service = PersistentMemoryService(db, state["user_id"], scope)
                memory_text = "\n" + memory_service.format_memory_for_llm(persistent_memory) + "\n"
        
        # Get personalized emphasis
        personalization = context.get("personalization", {})
        emphasis_text = ""
        if personalization:
            emphasis = personalization.get("emphasis", {})
            greeting = personalization.get("greeting", "")
            emphasis_text = (
                f"\n**Personalization Settings:**\n"
                f"Greeting: {greeting}\n"
                f"Detail Level: {emphasis.get('detail_level', 'balanced')}\n"
                f"Focus: {emphasis.get('focus', 'operational')}\n"
                f"Presentation: {emphasis.get('data_presentation', 'summary')}\n\n"
            )
        
        # Add schema info for nl_query intent
        schema_text = ""
        if state["intent"] == "nl_query":
            schema_info = context.get("schema_info", {})
            if schema_info:
                schema_text = (
                    f"\n**USER ACCESS SCOPE:**\n"
                    f"Realm ID: {schema_info.get('realm_id')}\n"
                    f"Role: {schema_info.get('role')}\n"
                )
                if schema_info.get('assigned_store_id'):
                    schema_text += f"Assigned Store ID: {schema_info['assigned_store_id']}\n"
                    schema_text += "**IMPORTANT**: This user can ONLY access data for their assigned store. Filter all queries by assigned_store_id.\n"
                else:
                    schema_text += "**IMPORTANT**: This user can access all stores in their realm. Filter all queries by realm_id.\n"
                schema_text += f"\n{schema_info.get('access_note', '')}\n\n"
        
        # Build comprehensive user prompt
        user_prompt = (
            f"{memory_text}"
            f"{schema_text}"
            f"{detailed_context_text}\n\n"
            f"{emphasis_text}"
            f"{history_text}"
            f"**Current User Request:**\n{state['user_input']}\n\n"
            f"**Available Analytics Data:** {', '.join(context.get('analytics_used', []))}\n\n"
            f"**Instructions:**\n"
            f"Provide a highly personalized response that:\n"
            f"1. Uses language appropriate for the user's role and data access level\n"
            f"2. References specific data points from the detailed analysis above\n"
            f"3. Builds on BOTH the recent conversation AND the persistent memory\n"
            f"4. Uses industry-appropriate terminology\n"
            f"5. Prioritizes insights matching the user's communication style and preferences\n"
            f"6. Acknowledges any data limitations transparently\n"
            f"7. Emphasizes content based on user's historical interests and decision patterns"
        )
        
        state["llm_response"] = LLMClient().generate(prompt, user_prompt)
        state["confidence"] = extract_confidence(state["llm_response"])
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"LLM Error: {error_detail}")
        
        state["error"] = f"LLM generation failed: {str(e)}"
        state["llm_response"] = (
            "I encountered an issue generating the response. "
            f"Error: {str(e)[:100]}\n\n"
            "Try asking a more specific question like:\n"
            "- 'Show me revenue at risk'\n"
            "- 'List products with low stock'\n"
            "- 'What products need reordering?'"
        )
        state["confidence"] = "low"
    
    return state


def format_response(state: CopilotState) -> CopilotState:
    response = state["llm_response"].strip()
    
    analytics_used = state.get("analytics_used", [])
    if analytics_used and "Based on:" not in response:
        analytics_formatted = ", ".join([a.replace("_", " ").title() for a in analytics_used])
        response += f"\n\n**Based on:** {analytics_formatted}"
    
    state["response"] = response
    state["metadata"] = {
        **state.get("metadata", {}),
        "confidence": state.get("confidence", "medium"),
        "analytics_used": analytics_used,
        "error": state.get("error"),
        "business_context_source": state["business_context"].get("source"),
    }
    return state


def extract_confidence(response: str) -> str:
    response_lower = response.lower()
    if "confidence: high" in response_lower or "confidence:** high" in response_lower:
        return "high"
    if "confidence: low" in response_lower or "confidence:** low" in response_lower:
        return "low"
    return "medium"


def build_graph():
    graph = StateGraph(CopilotState)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("fetch_business_context", add_business_context)
    graph.add_node("call_llm", call_llm)
    graph.add_node("format_response", format_response)
    graph.set_entry_point("classify_intent")
    graph.add_edge("classify_intent", "fetch_business_context")
    graph.add_edge("fetch_business_context", "call_llm")
    graph.add_edge("call_llm", "format_response")
    graph.add_edge("format_response", END)
    return graph.compile()


copilot_graph = build_graph()


def run_copilot_workflow(
    user_input: str,
    requested_intent: str | None,
    user_id: int,
    conversation_history: list[dict[str, str]] | None = None,
    metadata: dict[str, Any] | None = None,
    db: Session | None = None,
    scope=None,
) -> dict[str, Any]:
    state = copilot_graph.invoke(
        {
            "user_input": user_input,
            "requested_intent": requested_intent,
            "user_id": user_id,
            "conversation_history": conversation_history or [],
            "metadata": metadata or {},
            "db": db,
            "scope": scope,
        }
    )
    return {
        "intent": state["intent"],
        "response": state["response"],
        "metadata": state.get("metadata", {}),
        "confidence": state.get("confidence", "medium"),
    }
