import uuid
from datetime import datetime
import enum
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class TicketPriority(str, enum.Enum):
    Critical = 'Critical'
    High = 'High'
    Medium = 'Medium'
    Low = 'Low'

class TicketStatus(str, enum.Enum):
    Raised = 'Raised'
    Triaged = 'Triaged'
    InProgress = 'InProgress'
    Resolved = 'Resolved'

class Ticket(Base):
    __tablename__ = 'tickets'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    category_id: Mapped[str] = mapped_column(String(50), nullable=True)
    
    priority: Mapped[TicketPriority] = mapped_column(Enum(TicketPriority), default=TicketPriority.Medium)
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), default=TicketStatus.Raised)
    
    reporter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))

    timeline = relationship("TicketTimeline", backref="ticket", cascade="all, delete-orphan")

class TicketTimeline(Base):
    __tablename__ = 'ticket_timeline'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False)
    step_name: Mapped[str] = mapped_column(String(100), nullable=False)
    update_text: Mapped[str] = mapped_column(Text, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))

class Suggestion(Base):
    __tablename__ = 'suggestions'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    upvotes: Mapped[int] = mapped_column(Integer, default=0)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))
