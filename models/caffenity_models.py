from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Time, Integer, Float, Boolean, ForeignKey, Numeric, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base
from datetime import time, datetime
from typing import Optional

class Canteen(Base):

    __tablename__ = 'canteens'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class MenuItem(Base):

    __tablename__ = 'menu_items'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    canteen_id: Mapped[Optional[int]] = mapped_column(ForeignKey('canteens.id'))
    canteen = relationship("Canteen", backref="menu_items")
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    prep_time: Mapped[Optional[str]] = mapped_column(String(20))
    image_url: Mapped[Optional[str]] = mapped_column(Text)
    rating: Mapped[Optional[float]] = mapped_column(Numeric(2, 1), default=0)
    calories: Mapped[Optional[int]] = mapped_column(Integer)
    is_veg: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    is_special: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    in_stock: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    available_from: Mapped[Optional[time]] = mapped_column(Time)
    available_to: Mapped[Optional[time]] = mapped_column(Time)
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))


class Order(Base):

    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    canteen_id: Mapped[Optional[int]] = mapped_column(ForeignKey('canteens.id'))
    student_name: Mapped[str] = mapped_column(String(255), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[Optional[str]] = mapped_column(String(50), default='Placed')
    scheduled_time: Mapped[Optional[str]] = mapped_column(String(50))
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), default='UPI')
    payment_status: Mapped[Optional[str]] = mapped_column(String(50), default='Paid')
    special_note: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow)


class OrderItem(Base):

    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey('orders.id', ondelete='CASCADE'))
    menu_item_id: Mapped[Optional[int]] = mapped_column(ForeignKey('menu_items.id'))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_at_time_of_order: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    customizations: Mapped[Optional[str]] = mapped_column(Text)
