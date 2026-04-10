import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, Integer, Numeric, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class ArenaEvent(Base):
    __tablename__ = 'arena_events'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    organizer: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cover_image_url: Mapped[str] = mapped_column(Text, nullable=True)
    mode: Mapped[str] = mapped_column(String(50), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    fee: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    max_team_size: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default='Upcoming')
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    prize_pot: Mapped[str] = mapped_column(String(100), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    total_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    filled_capacity: Mapped[int] = mapped_column(Integer, default=0)
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default='{}')


class ArenaRegistration(Base):
    __tablename__ = 'arena_registrations'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('arena_events.id', ondelete='CASCADE'), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    team_name: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='Registered')
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))


class ArenaTeamSync(Base):
    __tablename__ = 'arena_team_sync'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('arena_events.id', ondelete='CASCADE'), nullable=False)
    requester_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    recipient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    tier: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default='Pending')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))
