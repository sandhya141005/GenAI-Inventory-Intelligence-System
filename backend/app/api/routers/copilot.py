from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import AccessScope, get_access_scope, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.copilot import (
    ChatHistoryConversation,
    ChatHistoryMessage,
    ChatHistoryResponse,
    ChatRequest,
    CopilotResponse,
    NLQueryRequest,
    RecommendationRequest,
)
from app.services.conversation_service import ConversationService
from app.services.langgraph_workflow import run_copilot_workflow


router = APIRouter(prefix="/copilot", tags=["copilot"])


@router.post("/chat", response_model=CopilotResponse)
def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    scope: AccessScope = Depends(get_access_scope),
    db: Session = Depends(get_db),
) -> CopilotResponse:
    conversation_service = ConversationService(db)
    conversation = conversation_service.get_or_create_conversation(current_user.id, payload.conversation_id, payload.message)
    conversation_service.add_message(conversation.id, "user", payload.message)
    history = conversation_service.get_recent_messages(conversation.id)

    result = run_copilot_workflow(
        user_input=payload.message,
        requested_intent="chat",
        user_id=current_user.id,
        conversation_history=history,
        db=db,
        scope=scope,
    )
    conversation_service.add_message(conversation.id, "assistant", result["response"], {
        "intent": result["intent"],
        "confidence": result.get("confidence", "medium"),
    })
    conversation_service.prune_old_conversations(current_user.id)
    db.commit()
    return CopilotResponse(conversation_id=conversation.id, **result)


@router.get("/history", response_model=ChatHistoryResponse)
def chat_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ChatHistoryResponse:
    conversation_service = ConversationService(db)
    conversations = conversation_service.list_conversations(current_user.id)

    return ChatHistoryResponse(
        conversations=[
            ChatHistoryConversation(
                conversation_id=conversation.id,
                title=conversation.title,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                messages=[
                    ChatHistoryMessage(
                        id=message.id,
                        role=message.role,
                        content=message.content,
                        created_at=message.created_at,
                        metadata=message.message_metadata,
                    )
                    for message in conversation.messages
                ],
            )
            for conversation in conversations
        ]
    )


@router.delete("/history/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_history(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    conversation_service = ConversationService(db)
    deleted = conversation_service.delete_conversation(current_user.id, conversation_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    db.commit()


@router.get("/morning-brief", response_model=CopilotResponse)
def morning_brief(
    current_user: User = Depends(get_current_user),
    scope: AccessScope = Depends(get_access_scope),
    db: Session = Depends(get_db),
) -> CopilotResponse:
    return CopilotResponse(
        **run_copilot_workflow(
            user_input="Create this morning's inventory operations brief.",
            requested_intent="morning_brief",
            user_id=current_user.id,
            db=db,
            scope=scope,
        )
    )


@router.get("/weekly-report", response_model=CopilotResponse)
def weekly_report(
    current_user: User = Depends(get_current_user),
    scope: AccessScope = Depends(get_access_scope),
    db: Session = Depends(get_db),
) -> CopilotResponse:
    return CopilotResponse(
        **run_copilot_workflow(
            user_input="Create the weekly inventory and revenue performance report.",
            requested_intent="weekly_report",
            user_id=current_user.id,
            db=db,
            scope=scope,
        )
    )


@router.get("/executive-summary", response_model=CopilotResponse)
def executive_summary(
    current_user: User = Depends(get_current_user),
    scope: AccessScope = Depends(get_access_scope),
    db: Session = Depends(get_db),
) -> CopilotResponse:
    return CopilotResponse(
        **run_copilot_workflow(
            user_input="Generate an executive summary of current inventory status.",
            requested_intent="executive_summary",
            user_id=current_user.id,
            db=db,
            scope=scope,
        )
    )


@router.post("/recommendations", response_model=CopilotResponse)
def recommendations(
    payload: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    scope: AccessScope = Depends(get_access_scope),
    db: Session = Depends(get_db),
) -> CopilotResponse:
    prompt = (
        f"Recommend inventory actions for focus_area={payload.focus_area or 'all operations'}, "
        f"horizon_days={payload.horizon_days}, constraints={payload.constraints}."
    )
    return CopilotResponse(
        **run_copilot_workflow(
            user_input=prompt,
            requested_intent="recommendations",
            user_id=current_user.id,
            db=db,
            scope=scope,
        )
    )


@router.post("/nl-query", response_model=CopilotResponse)
def nl_query(
    payload: NLQueryRequest,
    current_user: User = Depends(get_current_user),
    scope: AccessScope = Depends(get_access_scope),
    db: Session = Depends(get_db),
) -> CopilotResponse:
    return CopilotResponse(
        **run_copilot_workflow(
            user_input=payload.question,
            requested_intent="nl_query",
            user_id=current_user.id,
            metadata={"include_sql": payload.include_sql},
            db=db,
            scope=scope,
        )
    )
