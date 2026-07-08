"""
Enhanced Intent Classification Service
Uses pattern matching, keyword analysis, and context to accurately identify user intent.
"""
import re
from typing import Any


class IntentClassifier:
    def __init__(self):
        self.intent_patterns = {
            "nl_query": {
                "keywords": ["sql", "query", "database", "select", "table", "schema"],
                "phrases": [
                    "write a query",
                    "show me sql",
                    "database query",
                    "run a query",
                    "query for",
                    "in sql"
                ],
                "patterns": [
                    r"\bselect\b.*\bfrom\b",
                    r"\bwrite\s+(?:a\s+)?(?:sql\s+)?query\b",
                ],
                "priority": 10,
            },
            "root_cause_analysis": {
                "keywords": ["why", "reason", "cause", "explain", "analysis", "investigate"],
                "phrases": [
                    "root cause",
                    "why did",
                    "what caused",
                    "reason for",
                    "why is there",
                    "what happened",
                    "analyze why",
                    "investigate",
                ],
                "patterns": [
                    r"\bwhy\s+(?:did|is|are|was|were|has|have)\b",
                    r"\b(?:decrease|increase|drop|rise|spike|change).*why\b",
                    r"\bwhat\s+caused\b",
                    r"\broot\s+cause\b",
                ],
                "priority": 9,
            },
            "recommendations": {
                "keywords": ["recommend", "suggest", "advice", "action", "should"],
                "phrases": [
                    "what should i",
                    "recommend",
                    "suggestions",
                    "advice",
                    "what to do",
                    "what actions",
                    "how to fix",
                    "best course",
                ],
                "patterns": [
                    r"\b(?:what|how)\s+(?:should|can|do)\s+(?:i|we)\b",
                    r"\brecommend(?:ation)?s?\b",
                    r"\bsuggest(?:ion)?s?\b",
                    r"\bwhat\s+(?:to\s+)?(?:do|action)\b",
                ],
                "priority": 8,
            },
            "morning_brief": {
                "keywords": ["morning", "today", "brief", "daily"],
                "phrases": [
                    "morning brief",
                    "daily brief",
                    "today's brief",
                    "morning update",
                    "daily update",
                    "morning summary",
                    "start of day",
                ],
                "patterns": [
                    r"\bmorning\s+brief\b",
                    r"\b(?:today'?s?|daily)\s+(?:brief|update|summary)\b",
                    r"\bwhat'?s?\s+(?:happening\s+)?today\b",
                ],
                "priority": 9,
            },
            "weekly_report": {
                "keywords": ["weekly", "week", "report"],
                "phrases": [
                    "weekly report",
                    "week report",
                    "this week",
                    "past week",
                    "weekly summary",
                    "week summary",
                ],
                "patterns": [
                    r"\bweekly\s+(?:report|summary)\b",
                    r"\b(?:this|past|last)\s+week\b.*(?:report|summary)\b",
                ],
                "priority": 9,
            },
            "executive_summary": {
                "keywords": ["executive", "summary", "overview", "high-level"],
                "phrases": [
                    "executive summary",
                    "high level",
                    "overall summary",
                    "business overview",
                    "overall status",
                    "big picture",
                ],
                "patterns": [
                    r"\bexecutive\s+summary\b",
                    r"\b(?:high.?level|overall)\s+(?:summary|overview|status)\b",
                    r"\bbig\s+picture\b",
                ],
                "priority": 9,
            },
        }
    
    def classify(self, user_input: str, conversation_history: list[dict[str, str]] | None = None) -> str:
        """
        Classify user intent using multiple signals.
        
        Returns:
            Intent string (e.g., "recommendations", "morning_brief", "inventory_agent")
        """
        text = user_input.lower().strip()
        
        if not text:
            return "inventory_agent"
        
        scores = {}
        
        for intent, config in self.intent_patterns.items():
            score = 0
            
            for keyword in config["keywords"]:
                if keyword in text:
                    score += 1
            
            for phrase in config["phrases"]:
                if phrase in text:
                    score += 3
            
            for pattern in config["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 4
            
            if score > 0:
                score *= config["priority"]
                scores[intent] = score
        
        if conversation_history:
            scores = self._adjust_for_context(scores, conversation_history)
        
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return self._classify_by_question_type(text)
    
    def _adjust_for_context(self, scores: dict[str, int], history: list[dict[str, str]]) -> dict[str, int]:
        """Adjust scores based on conversation context."""
        if not history:
            return scores
        
        recent_messages = history[-3:]
        context_text = " ".join([msg.get("content", "").lower() for msg in recent_messages])
        
        if "recommend" in context_text or "suggest" in context_text:
            if "recommendations" in scores:
                scores["recommendations"] += 2
        
        if "why" in context_text or "cause" in context_text:
            if "root_cause_analysis" in scores:
                scores["root_cause_analysis"] += 2
        
        return scores
    
    def _classify_by_question_type(self, text: str) -> str:
        """Fallback classification based on question structure."""
        question_patterns = {
            "recommendations": [
                r"^(?:what|how)\s+(?:should|can|could|do)\s+(?:i|we)\b",
                r"^(?:can|could)\s+you\s+(?:recommend|suggest)\b",
            ],
            "root_cause_analysis": [
                r"^why\s+",
                r"^what\s+(?:caused|happened|went\s+wrong)\b",
            ],
            "nl_query": [
                r"^(?:show|give|get|fetch|retrieve|list)\s+(?:me\s+)?(?:all|the)?\s+\w+\s+(?:from|in|where)\b",
            ],
        }
        
        for intent, patterns in question_patterns.items():
            for pattern in patterns:
                if re.match(pattern, text, re.IGNORECASE):
                    return intent
        
        if self._is_data_request(text):
            return "inventory_agent"
        
        if self._is_action_request(text):
            return "recommendations"
        
        return "inventory_agent"
    
    def _is_data_request(self, text: str) -> bool:
        """Check if user is requesting specific data."""
        data_verbs = [
            "show", "list", "display", "get", "find", "search",
            "view", "see", "check", "look", "tell me", "what is",
            "how many", "how much"
        ]
        return any(verb in text for verb in data_verbs)
    
    def _is_action_request(self, text: str) -> bool:
        """Check if user is requesting action/recommendations."""
        action_indicators = [
            "should i", "what to do", "how to", "help me",
            "need to", "want to", "trying to", "looking to"
        ]
        return any(indicator in text for indicator in action_indicators)
    
    def get_intent_confidence(self, user_input: str, detected_intent: str) -> float:
        """
        Calculate confidence score for detected intent (0.0 to 1.0).
        """
        text = user_input.lower().strip()
        
        if detected_intent not in self.intent_patterns:
            return 0.5
        
        config = self.intent_patterns[detected_intent]
        matches = 0
        max_possible = len(config["keywords"]) + len(config["phrases"]) + len(config["patterns"])
        
        if max_possible == 0:
            return 0.5
        
        for keyword in config["keywords"]:
            if keyword in text:
                matches += 1
        
        for phrase in config["phrases"]:
            if phrase in text:
                matches += 1
        
        for pattern in config["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1
        
        confidence = min(matches / max_possible * 2, 1.0)
        return max(confidence, 0.3)
