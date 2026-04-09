import uuid
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime, timezone
from database import Base

class User_Refresh_Token(Base):
    __tablename__ = "user_refresh_token"

    token_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Admin_Refresh_Token(Base):
    __tablename__ = "admin_refresh_token"

    token_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column(Integer)
    token: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))