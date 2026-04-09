from sqlalchemy import Integer, Column, String, VARCHAR, Text, DATE, FLOAT, DateTime
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
from database import Base


class User_Refresh_Token(Base):

    __tablename__ = "user_refresh_token"

    token_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer)
    token: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime)


class Admin_Refresh_Token(Base):

    __tablename__ = "admin_refresh_token"

    token_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column(Integer)
    token: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime)