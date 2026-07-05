from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

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


def classify_intent(state: CopilotState) -> CopilotState:
    requested = state.get("requested_intent")
    if requested and requested != "chat":
        state["intent"] = requested
        return state

    text = state["user_input"].lower()
    if "root cause" in text or "why" in text:
        intent = "root_cause_analysis"
    elif "recommend" in text or "action" in text:
        intent = "recommendations"
    elif "sql" in text or "query" in text:
        intent = "nl_query"
    elif "weekly" in text:
        intent = "weekly_report"
    elif "morning" in text or "brief" in text:
        intent = "morning_brief"
    else:
        intent = "executive_summary"
    state["intent"] = intent
    return state


def add_business_context(state: CopilotState) -> CopilotState:
    state["business_context"] = fetch_business_context(
        intent=state["intent"],
        user_input=state["user_input"],
        user_id=state["user_id"],
    )
    return state


def call_llm(state: CopilotState) -> CopilotState:
    prompt = load_prompt(state["intent"])
    history = state.get("conversation_history", [])
    user_prompt = (
        f"User request:\n{state['user_input']}\n\n"
        f"Conversation history:\n{history}\n\n"
        f"Business context:\n{state['business_context']}\n\n"
        f"Metadata:\n{state.get('metadata', {})}"
    )
    state["llm_response"] = LLMClient().generate(prompt, user_prompt)
    return state


def format_response(state: CopilotState) -> CopilotState:
    state["response"] = state["llm_response"].strip()
    state["metadata"] = {
        **state.get("metadata", {}),
        "business_context_source": state["business_context"].get("source"),
        "member3_handoff": state["business_context"].get("member3_handoff"),
    }
    return state


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
) -> dict[str, Any]:
    state = copilot_graph.invoke(
        {
            "user_input": user_input,
            "requested_intent": requested_intent,
            "user_id": user_id,
            "conversation_history": conversation_history or [],
            "metadata": metadata or {},
        }
    )
    return {"intent": state["intent"], "response": state["response"], "metadata": state.get("metadata", {})}
