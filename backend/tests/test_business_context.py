import pytest
from unittest.mock import Mock, patch

from app.services.business_context import fetch_business_context


def test_fetch_business_context_executive_summary(db_session):
    with patch("app.services.business_context.AnalyticsService") as mock_analytics:
        mock_analytics_instance = Mock()
        mock_analytics_instance.overview.return_value = {"kpis": []}
        mock_analytics.return_value = mock_analytics_instance
        
        context = fetch_business_context(
            intent="executive_summary",
            user_input="Show me the executive summary",
            user_id=1,
            db=db_session
        )
        
        assert context["intent"] == "executive_summary"
        assert "overview" in context
        assert "analytics_used" in context
        assert "overview" in context["analytics_used"]


def test_fetch_business_context_morning_brief(db_session):
    with patch("app.services.business_context.AnalyticsService") as mock_analytics:
        mock_analytics_instance = Mock()
        mock_analytics_instance.overview.return_value = {"kpis": []}
        mock_analytics_instance.notices.return_value = {"notices": []}
        mock_analytics_instance.inventory.return_value = {"items": []}
        mock_analytics.return_value = mock_analytics_instance
        
        context = fetch_business_context(
            intent="morning_brief",
            user_input="Give me the morning brief",
            user_id=1,
            db=db_session
        )
        
        assert context["intent"] == "morning_brief"
        assert "overview" in context
        assert "notices" in context
        assert "inventory" in context
        assert len(context["analytics_used"]) >= 3


def test_fetch_business_context_recommendations(db_session):
    with patch("app.services.business_context.AnalyticsService") as mock_analytics:
        mock_analytics_instance = Mock()
        mock_analytics_instance.recommendations.return_value = {"recommendations": []}
        mock_analytics_instance.overview.return_value = {"kpis": []}
        mock_analytics.return_value = mock_analytics_instance
        
        context = fetch_business_context(
            intent="recommendations",
            user_input="What should I do?",
            user_id=1,
            db=db_session
        )
        
        assert context["intent"] == "recommendations"
        assert "recommendations" in context
        assert "overview" in context


def test_fetch_business_context_with_transfer_keyword(db_session):
    with patch("app.services.business_context.AnalyticsService") as mock_analytics:
        mock_analytics_instance = Mock()
        mock_analytics_instance.transfers.return_value = {"transfers": []}
        mock_analytics_instance.overview.return_value = {"kpis": []}
        mock_analytics_instance.inventory.return_value = {"items": []}
        mock_analytics.return_value = mock_analytics_instance
        
        context = fetch_business_context(
            intent="chat",
            user_input="Show me transfer recommendations",
            user_id=1,
            db=db_session
        )
        
        assert "transfers" in context
        assert "transfers" in context["analytics_used"]


def test_fetch_business_context_error_handling(db_session):
    with patch("app.services.business_context.AnalyticsService") as mock_analytics:
        mock_analytics.return_value.overview.side_effect = Exception("Database error")
        
        context = fetch_business_context(
            intent="executive_summary",
            user_input="Show me the summary",
            user_id=1,
            db=db_session
        )
        
        assert "error" in context
        assert context.get("partial_failure") is True
