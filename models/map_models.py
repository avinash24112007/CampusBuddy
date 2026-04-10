from sqlalchemy import String, Text, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from typing import Optional


class Building(Base):
    """Maps to frontend BUILDINGS array used by the 3D mapping engine."""
    __tablename__ = 'buildings'

    id: Mapped[str] = mapped_column(String(50), primary_key=True)          # e.g. 'uid', 'dome', 'mess'
    name: Mapped[str] = mapped_column(String(255), nullable=False)         # "UID – Design Block"
    short_code: Mapped[str] = mapped_column(String(10), nullable=False)    # "UID"
    floors: Mapped[list[int]] = mapped_column(ARRAY(Integer), server_default='{}')
    x: Mapped[float] = mapped_column(Float, default=0.0)
    z: Mapped[float] = mapped_column(Float, default=0.0)
    w: Mapped[float] = mapped_column(Float, default=0.0)                   # width
    d: Mapped[float] = mapped_column(Float, default=0.0)                   # depth
    status: Mapped[str] = mapped_column(String(50), default='available')   # available, high-traffic, live-event
    facilities: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text), server_default='{}')


class Room(Base):
    """Maps to frontend ROOMS dictionary, indexed by building_id."""
    __tablename__ = 'rooms'

    id: Mapped[str] = mapped_column(String(50), primary_key=True)          # e.g. 'UID-101'
    building_id: Mapped[str] = mapped_column(String(50), nullable=False)   # FK-like ref to buildings.id
    name: Mapped[str] = mapped_column(String(255), nullable=False)         # "Design Studio 1"
    floor: Mapped[str] = mapped_column(String(10), nullable=False)         # "1F", "GF"
    capacity: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default='Available')   # Available, Occupied, Live Event
    booked_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class LiveMarker(Base):
    """Floating notifications / shop / event location markers for the 3D map."""
    __tablename__ = 'live_markers'

    id: Mapped[str] = mapped_column(String(50), primary_key=True)          # e.g. 'm1', 'm2'
    type: Mapped[str] = mapped_column(String(50), nullable=False)          # cafeteria, event, shop, problem
    building_id: Mapped[str] = mapped_column(String(50), nullable=False)   # ref to buildings.id
    pulse_color: Mapped[str] = mapped_column(String(20), default='Blue')   # Red, Orange, Blue, Green
