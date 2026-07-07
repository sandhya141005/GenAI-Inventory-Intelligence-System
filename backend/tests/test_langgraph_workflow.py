import pytest
from unittest.mock import Mock, patch

from app.services.langgraph_workflow import (
    classify_intent,
    extract_confidence,
    run_copilot_workflow,
)


def test_classify_intent_root_cause():
    state = {
        "user_input": "Why did revenue decrease last week?",
        "requested_intent": None,
    }
    result = classify_intent(state)
    assert result["intent"] == "root_cause_analysis"


def test_classify_intent_recommendations():
    state = {
        "user_input": "What actions should I take?",
        "requested_intent": None,
    }
    result = classify_intent(state)
    assert result["intent"] == "recommendations"


def test_classify_intent_morning_brief():
    state = {
        "user_input": "Give me today's morning brief",
        "requested_intent": None,
    }
    result = classify_intent(state)
    assert result["intent"] == "morning_brief"


def test_classify_intent_weekly_report():
    state = {
        "user_input": "Generate the weekly report",
        "requested_intent": None,
    }
    result = classify_intent(state)
    assert result["intent"] == "weekly_report"


def test_classify_intent_inventory_agent():
    state = {
        "user_input": "Which products will stock out?",
        "requested_intent": None,
    }
    result = classify_intent(state)
    assert result["intent"] == "inventory_agent"


def test_classify_intent_forced():
    state = {
        "user_input": "Some random text",
        "requested_intent": "executive_summary",
    }
    result = classify_intent(state)
    assert result["intent"] == "executive_summary"


def test_extract_confidence_high():
    response = "Some text\n**Confidence:** High\nMore text"
    assert extract_confidence(response) == "high"


def test_extract_confidence_low():
    response = "Some text\nConfidence: low\nMore text"
    assert extract_confidence(response) == "low"


def test_extract_confidence_default():
    response = "Some text without confidence"
    assert extract_confidence(response) == "medium"


@pytest.mark.parametrize("user_input,expected_intent", [
    ("Which warehouse has excess inventory?", "inventory_agent"),
    ("Why did sales drop?", "root_cause_analysis"),
    ("Recommend actions", "recommendations"),
    ("Morning brief", "morning_brief"),
    ("Weekly summary", "weekly_report"),
    ("Show me SQL query", "nl_query"),
])
def test_intent_classification_variations(user_input, expected_intent):
    state = {
        "user_input": user_input,
        "requested_intent": None,
    }
    result = classify_intent(state)
    assert result["intent"] == expected_intent


def test_run_copilot_workflow_integration(db_session, mock_llm_response):
    with patch("app.services.langgraph_workflow.LLMClient") as mock_llm:
        with patch("app.services.langgraph_workflow.fetch_business_context") as mock_context:
            mock_llm_instance = Mock()
            mock_llm_instance.generate.return_value = mock_llm_response
            mock_llm.return_value = mock_llm_instance
            
            mock_context.return_value = {
                "intent": "inventory_agent",
                "analytics_used": ["overview", "inventory"],
                "overview": {"kpis": []},
                "inventory": {"items": []},
            }
            
            result = run_copilot_workflow(
                user_input="Show me stockout risks",
                requested_intent="chat",
                user_id=1,
                db=db_session
            )
            
            assert "intent" in result
            assert "response" in result
            assert "confidence" in result
            assert "metadata" in result
            assert result["confidence"] == "high"


def test_run_copilot_workflow_error_handling(db_session):
    with patch("app.services.langgraph_workflow.fetch_business_context") as mock_context:
        mock_context.side_effect = Exception("Database connection failed")
        
        result = run_copilot_workflow(
            user_input="Show me the data",
            requested_intent="chat",
            user_id=1,
            db=db_session
        )
        
        assert "response" in result
        assert "encountered an issue" in result["response"].lower()
        assert result["confidence"] == "low"
