from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message


class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_conversation(self, user_id: int, conversation_id: int | None, first_message: str) -> Conversation:
        if conversation_id:
            conversation = self.db.scalar(
                select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
            )
            if conversation:
                return conversation

        title = first_message[:80]
        conversation = Conversation(user_id=user_id, title=title)
        self.db.add(conversation)
        self.db.flush()
        return conversation

    def add_message(self, conversation_id: int, role: str, content: str, metadata: dict | None = None) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            message_metadata=metadata,
        )
        self.db.add(message)
        self.db.flush()
        return message

    def get_recent_messages(self, conversation_id: int, limit: int = 12) -> list[dict[str, str]]:
        rows = self.db.scalars(
            select(Message).where(Message.conversation_id == conversation_id).order_by(Message.id.desc()).limit(limit)
        ).all()
        return [{"role": row.role, "content": row.content} for row in reversed(rows)]
