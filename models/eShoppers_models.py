from sqlalchemy import Integer, Column, String, VARCHAR, Text, DATE, FLOAT
from sqlalchemy. dialects.postgresql import ARRAY
from sqlalchemy. orm import mapped_column, Mapped
from datetime import datetime, date
from sqlalchemy import Float
from database import Base

class E_Store(Base):

    __tablename__ = "e_Store"
    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)

    name : Mapped[str] = mapped_column(String)

    catagory: Mapped[str] = mapped_column(String)

    Price: Mapped[float] = mapped_column(FLOAT, default = 0.0)

    stock: Mapped[int] = mapped_column()

    vendor: Mapped[str] = mapped_column(String)

    finPrice: Mapped[float] = mapped_column(FLOAT, default = 0.0)

    rating: Mapped[float] = mapped_column(FLOAT, default = 0.0)

