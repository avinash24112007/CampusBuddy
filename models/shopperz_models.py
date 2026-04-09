import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, Integer, Numeric, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class RetailInventory(Base):
    __tablename__ = 'retail_inventory'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    stock_level: Mapped[int] = mapped_column(Integer, default=0)
    image_url: Mapped[str] = mapped_column(Text, nullable=True)
    is_duo_sync: Mapped[bool] = mapped_column(Boolean, default=False)
    duo_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    rating: Mapped[float] = mapped_column(Numeric(2, 1), default=0.0)
    reviews: Mapped[int] = mapped_column(Integer, default=0)
    # Revenue tracker requested by user
    total_sales: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)

class MarketListing(Base):
    __tablename__ = 'market_listings'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    seller_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    seller = relationship("User")
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    original_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    image_url: Mapped[str] = mapped_column(Text, nullable=True)
    condition: Mapped[str] = mapped_column(String(20), nullable=False)  # 'New', 'Good', 'Used'
    status: Mapped[str] = mapped_column(String(20), default='Available')  # 'Available', 'Reserved', 'Sold'
    reservation_expiry: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
class PrintQueue(Base):
    __tablename__ = 'print_queue'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    file_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default='{}')
    cost_total: Mapped[float] = mapped_column(Numeric(8, 2), default=0.0)
    status: Mapped[str] = mapped_column(String(20), default='Queued')  # 'Queued', 'In_Process', 'Ready'
