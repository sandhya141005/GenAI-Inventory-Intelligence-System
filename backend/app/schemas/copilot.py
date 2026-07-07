from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: int | None = None


class RecommendationRequest(BaseModel):
    focus_area: str | None = Field(default=None, max_length=120)
    horizon_days: int = Field(default=14, ge=1, le=90)
    constraints: list[str] = Field(default_factory=list)


class NLQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    include_sql: bool = True


class CopilotResponse(BaseModel):
    intent: str
    response: str
    conversation_id: int | None = None
    metadata: dict = Field(default_factory=dict)
    confidence: str = Field(default="medium")


class ChatHistoryMessage(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    metadata: dict | None = None


class ChatHistoryConversation(BaseModel):
    conversation_id: int
    title: str | None = None
    created_at: datetime
    updated_at: datetime
    messages: list[ChatHistoryMessage] = Field(default_factory=list)


class ChatHistoryResponse(BaseModel):
    conversations: list[ChatHistoryConversation] = Field(default_factory=list)
