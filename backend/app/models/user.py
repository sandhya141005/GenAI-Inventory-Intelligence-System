from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


WAREHOUSE_OWNER = "WAREHOUSE_OWNER"
STORE_MANAGER = "STORE_MANAGER"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    realm_id: Mapped[int | None] = mapped_column(ForeignKey("realms.id"), index=True, nullable=True)
    role: Mapped[str | None] = mapped_column(String(32), nullable=True)
    assigned_store_id: Mapped[int | None] = mapped_column(ForeignKey("stores.store_id"), index=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    realm = relationship("Realm", foreign_keys=[realm_id], back_populates="users")
    assigned_store = relationship("Store")


class Realm(Base):
    __tablename__ = "realms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry_tag: Mapped[str] = mapped_column(String(120), nullable=False)
    join_code: Mapped[str] = mapped_column(String(4), unique=True, index=True, nullable=False)
    owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    users = relationship("User", foreign_keys=[User.realm_id], back_populates="realm")
    owner = relationship("User", foreign_keys=[owner_user_id])
