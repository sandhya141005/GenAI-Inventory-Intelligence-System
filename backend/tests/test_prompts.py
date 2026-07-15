import pytest
from pathlib import Path

from app.services.prompt_service import PROMPT_DIR, load_prompt


def test_prompt_directory_exists():
    assert PROMPT_DIR.exists()
    assert PROMPT_DIR.is_dir()


def test_all_prompts_exist():
    required_prompts = [
        "executive_summary.md",
        "morning_brief.md",
        "weekly_report.md",
        "recommendations.md",
        "root_cause_analysis.md",
        "nl_to_sql.md",
        "inventory_agent.md",
    ]
    
    for prompt_file in required_prompts:
        prompt_path = PROMPT_DIR / prompt_file
        assert prompt_path.exists(), f"Missing prompt file: {prompt_file}"
        assert prompt_path.stat().st_size > 0, f"Empty prompt file: {prompt_file}"


def test_load_prompt_executive_summary():
    content = load_prompt("executive_summary")
    assert len(content) > 100
    assert "executive" in content.lower() or "summary" in content.lower()


def test_load_prompt_morning_brief():
    content = load_prompt("morning_brief")
    assert len(content) > 100
    assert "morning" in content.lower() or "brief" in content.lower()


def test_load_prompt_weekly_report():
    content = load_prompt("weekly_report")
    assert len(content) > 100
    assert "weekly" in content.lower() or "report" in content.lower()


def test_load_prompt_recommendations():
    content = load_prompt("recommendations")
    assert len(content) > 100
    assert "recommend" in content.lower() or "action" in content.lower()


def test_load_prompt_root_cause():
    content = load_prompt("root_cause_analysis")
    assert len(content) > 100
    assert "root cause" in content.lower() or "analysis" in content.lower()


def test_load_prompt_inventory_agent():
    content = load_prompt("inventory_agent")
    assert len(content) > 100
    assert "inventory" in content.lower() or "agent" in content.lower()


def test_load_prompt_chat_default():
    content = load_prompt("chat")
    assert len(content) > 100


def test_load_prompt_unknown_intent():
    content = load_prompt("unknown_intent_xyz")
    assert len(content) > 0


def test_prompt_quality_checks():
    prompts_to_check = [
        ("executive_summary", ["confidence", "data", "action"]),
        ("morning_brief", ["priority", "today", "action"]),
        ("weekly_report", ["week", "performance", "trend"]),
        ("recommendations", ["action", "impact", "priority"]),
        ("root_cause_analysis", ["cause", "evidence", "hypothesis"]),
        ("inventory_agent", ["inventory", "answer", "data"]),
    ]
    
    for intent, keywords in prompts_to_check:
        content = load_prompt(intent).lower()
        for keyword in keywords:
            assert keyword in content, f"Prompt '{intent}' missing keyword '{keyword}'"


def test_prompts_have_structure():
    prompts_needing_structure = [
        "executive_summary",
        "morning_brief",
        "weekly_report",
        "recommendations",
        "root_cause_analysis",
    ]
    
    for intent in prompts_needing_structure:
        content = load_prompt(intent)
        assert "#" in content or "**" in content, f"Prompt '{intent}' lacks markdown structure"
