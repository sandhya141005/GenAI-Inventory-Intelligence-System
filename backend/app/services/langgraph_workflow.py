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

    text = state["user_input"].lower()
    
    if "root cause" in text or ("why" in text and ("decrease" in text or "increase" in text or "drop" in text)):
        intent = "root_cause_analysis"
    elif "recommend" in text or "action" in text or "should i" in text or "what to do" in text:
        intent = "recommendations"
    elif "sql" in text or "query" in text or "database" in text:
        intent = "nl_query"
    elif "weekly" in text and ("report" in text or "summary" in text):
        intent = "weekly_report"
    elif ("morning" in text or "brief" in text or "today" in text) and ("summary" in text or "brief" in text):
        intent = "morning_brief"
    elif "executive" in text or "summary" in text or "overview" in text:
        intent = "executive_summary"
    else:
        intent = "inventory_agent"
    
    state["intent"] = intent
    return state


def add_business_context(state: CopilotState) -> CopilotState:
    try:
        db = state.get("db") or next(get_db())
        state["business_context"] = fetch_business_context(
            intent=state["intent"],
            user_input=state["user_input"],
            user_id=state["user_id"],
            db=db,
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
        prompt = load_prompt(state["intent"])
        history = state.get("conversation_history", [])
        
        history_text = ""
        if history:
            history_text = "Previous conversation:\n"
            for msg in history[-6:]:
                history_text += f"{msg['role']}: {msg['content'][:200]}\n"
        
        # Simplify business context to avoid token limits
        context = state['business_context']
        simplified_context = {}
        
        # Only include non-dict values and summaries
        for key, value in context.items():
            if key in ['as_of', 'intent', 'user_id', 'source', 'query', 'analytics_used', 'error', 'partial_failure']:
                simplified_context[key] = value
            elif isinstance(value, dict):
                # For overview, extract just summary
                if key == 'overview' and 'summary' in value:
                    simplified_context[key] = {
                        'summary': value['summary'],
                        'kpi_count': len(value.get('kpis', [])),
                        'recommendation_count': len(value.get('recommendations', []))
                    }
                # For other dicts, just count items
                elif isinstance(value, dict):
                    simplified_context[f"{key}_available"] = True
                    if 'items' in value:
                        simplified_context[f"{key}_count"] = len(value['items'])
                    elif key.endswith('s'):  # plural keys like 'recommendations', 'transfers'
                        # Try to get the list
                        for subkey, subvalue in value.items():
                            if isinstance(subvalue, list):
                                simplified_context[f"{key}_count"] = len(subvalue)
                                break
        
        user_prompt = (
            f"User request:\n{state['user_input']}\n\n"
            f"{history_text}\n"
            f"Context summary: {simplified_context}\n\n"
            f"Full data available: {', '.join(state['business_context'].get('analytics_used', []))}\n"
            f"Respond based on the available analytics data. If you need specific details, "
            f"acknowledge what data is available and provide insights based on that."
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
) -> dict[str, Any]:
    state = copilot_graph.invoke(
        {
            "user_input": user_input,
            "requested_intent": requested_intent,
            "user_id": user_id,
            "conversation_history": conversation_history or [],
            "metadata": metadata or {},
            "db": db,
        }
    )
    return {
        "intent": state["intent"],
        "response": state["response"],
        "metadata": state.get("metadata", {}),
        "confidence": state.get("confidence", "medium"),
    }
