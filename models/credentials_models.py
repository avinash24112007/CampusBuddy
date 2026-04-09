from sqlalchemy import Integer, Column, String, VARCHAR, Text
from sqlalchemy.orm import mapped_column, Mapped
from database import Base

class Admin_Credentials(Base):
    __tablename__ = 'admin_credentials'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String)

    email: Mapped[str] = mapped_column(String)

    password: Mapped[str] = mapped_column(String)

    role: Mapped[str] = mapped_column(String)