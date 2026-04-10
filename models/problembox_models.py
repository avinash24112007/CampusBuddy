import uuid
import random
from datetime import datetime
import enum
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, text, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
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

def generate_tkt_id():
    return f"TKT-{random.randint(1000, 9999)}"

class Ticket(Base):
    __tablename__ = 'tickets'

    id: Mapped[str] = mapped_column(String(20), primary_key=True, default=generate_tkt_id)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    category_id: Mapped[str] = mapped_column(String(50), nullable=True)
    
    priority: Mapped[TicketPriority] = mapped_column(Enum(TicketPriority), default=TicketPriority.Medium)
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), default=TicketStatus.Raised)
    
    reporter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reporter = relationship("User", foreign_keys=[reporter_id])
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)
    
    upvotes: Mapped[int] = mapped_column(Integer, default=0)
    has_resolved_viewed: Mapped[bool] = mapped_column(Boolean, default=False)
    media: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))

    timeline = relationship("TicketTimeline", backref="ticket", cascade="all, delete-orphan")

class TicketTimeline(Base):
    __tablename__ = 'ticket_timeline'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    ticket_id: Mapped[str] = mapped_column(ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False)
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
