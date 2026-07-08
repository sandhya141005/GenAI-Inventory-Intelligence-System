from pathlib import Path

from app.models.user import STORE_MANAGER, WAREHOUSE_OWNER


PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


def load_prompt(intent: str, role: str | None = None, industry: str | None = None) -> str:
    """
    Load role and industry-specific prompt with fallback chain.
    
    Fallback order:
    1. Role-specific prompt (e.g., prompts/recommendations/warehouse_owner.md)
    2. Generic prompt for intent (e.g., prompts/recommendations.md) - DEPRECATED
    3. Default inventory agent prompt
    """
    prompt_map = {
        "executive_summary": "executive_summary",
        "morning_brief": "morning_brief",
        "weekly_report": "weekly_report",
        "root_cause_analysis": "root_cause_analysis",
        "recommendations": "recommendations",
        "nl_query": "nl_to_sql",
        "chat": "inventory_agent",
        "inventory_agent": "inventory_agent",
    }
    
    intent_name = prompt_map.get(intent, "inventory_agent")
    
    if intent == "nl_query":
        return (PROMPT_DIR / "nl_to_sql.md").read_text(encoding="utf-8")
    
    if role:
        role_filename = _get_role_filename(role)
        role_specific_path = PROMPT_DIR / intent_name / f"{role_filename}.md"
        
        if role_specific_path.exists():
            prompt_content = role_specific_path.read_text(encoding="utf-8")
            return _apply_industry_personalization(prompt_content, industry)
    
    default_path = PROMPT_DIR / intent_name / "warehouse_owner.md"
    if default_path.exists():
        prompt_content = default_path.read_text(encoding="utf-8")
        return _apply_industry_personalization(prompt_content, industry)
    
    fallback_path = PROMPT_DIR / "inventory_agent" / "warehouse_owner.md"
    if fallback_path.exists():
        return fallback_path.read_text(encoding="utf-8")
    
    return "You are an inventory management assistant. Provide helpful, data-driven responses."


def _get_role_filename(role: str) -> str:
    """Convert role constant to filename."""
    if role == WAREHOUSE_OWNER:
        return "warehouse_owner"
    elif role == STORE_MANAGER:
        return "store_manager"
    return "warehouse_owner"


def _apply_industry_personalization(prompt_content: str, industry: str | None) -> str:
    """Apply industry-specific terminology to prompt."""
    if not industry:
        return prompt_content
    
    industry_terminology = _get_industry_terminology(industry)
    
    for placeholder, replacement in industry_terminology.items():
        prompt_content = prompt_content.replace(placeholder, replacement)
    
    return prompt_content


def _get_industry_terminology(industry: str) -> dict[str, str]:
    """Get industry-specific terminology replacements."""
    food_industries = [
        "Food & Beverage", "Groceries", "FMCG", "Packaged Foods",
        "Frozen Foods", "Organic Foods", "Specialty Foods", "Bakery",
        "Dairy", "Meat & Seafood", "Beverages", "Confectionery",
    ]
    
    pharma_industries = [
        "Pharmaceuticals", "Pharmacy Retail", "Medical Devices", "Health & Wellness"
    ]
    
    electronics_industries = [
        "Electronics", "Consumer Electronics", "Mobile Accessories",
        "Computer Hardware", "Electricals", "Telecom Equipment"
    ]
    
    if industry in food_industries:
        return {
            "{{industry}}": industry,
            "{{product_term}}": "food products and groceries",
            "{{expiry_context}}": "Pay special attention to shelf life, use-by dates, and FIFO (First In, First Out) rotation practices.",
            "{{storage_context}}": "Consider refrigerated, frozen, and ambient storage requirements.",
        }
    
    if industry in pharma_industries:
        return {
            "{{industry}}": industry,
            "{{product_term}}": "pharmaceutical products and medicines",
            "{{expiry_context}}": "Pay critical attention to expiration dates, beyond-use dates, and batch traceability for regulatory compliance.",
            "{{storage_context}}": "Consider controlled temperature storage and regulatory requirements.",
        }
    
    if industry in electronics_industries:
        return {
            "{{industry}}": industry,
            "{{product_term}}": "electronic products and devices",
            "{{expiry_context}}": "Pay attention to product lifecycle, technology obsolescence, and warranty periods.",
            "{{storage_context}}": "Consider climate-controlled storage and anti-static requirements.",
        }
    
    return {
        "{{industry}}": industry or "Retail",
        "{{product_term}}": "products",
        "{{expiry_context}}": "",
        "{{storage_context}}": "",
    }
