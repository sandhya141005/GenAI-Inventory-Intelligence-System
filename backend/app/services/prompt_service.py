from functools import lru_cache
from pathlib import Path


PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


@lru_cache
def load_prompt(intent: str) -> str:
    prompt_map = {
        "executive_summary": "executive_summary.md",
        "morning_brief": "morning_brief.md",
        "weekly_report": "weekly_report.md",
        "root_cause_analysis": "root_cause_analysis.md",
        "recommendations": "recommendations.md",
        "nl_query": "nl_to_sql.md",
        "chat": "executive_summary.md",
    }
    filename = prompt_map.get(intent, "executive_summary.md")
    return (PROMPT_DIR / filename).read_text(encoding="utf-8")
