from datetime import datetime, timezone

from sqlalchemy import delete, select
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
        conversation = self.db.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.now(timezone.utc)

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

    def list_conversations(self, user_id: int, limit: int = 5) -> list[Conversation]:
        return list(
            self.db.scalars(
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(Conversation.updated_at.desc(), Conversation.id.desc())
                .limit(limit)
            ).all()
        )

    def delete_conversation(self, user_id: int, conversation_id: int) -> bool:
        result = self.db.execute(
            delete(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        )
        return bool(result.rowcount)

    def prune_old_conversations(self, user_id: int, keep: int = 5) -> None:
        conversation_ids = self.db.scalars(
            select(Conversation.id)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc(), Conversation.id.desc())
            .offset(keep)
        ).all()
        if conversation_ids:
            self.db.execute(delete(Conversation).where(Conversation.id.in_(conversation_ids)))
