from sqlalchemy import Integer, Column, String, VARCHAR, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import mapped_column, Mapped
from database import Base

class User_Credentials(Base):
    __tablename__ = 'user_credentials'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String)

    email: Mapped[str] = mapped_column(String, index=True)

    password: Mapped[str] = mapped_column(String)

    type: Mapped[str] = mapped_column(default='Basic')

    balance: Mapped[int] = mapped_column(default=0)

    description: Mapped[str] = mapped_column(String)

    skills: Mapped[list[str]] = mapped_column(ARRAY(String))




class Admin_Credentials(Base):
    __tablename__ = 'admin_credentials'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String)

    email: Mapped[str] = mapped_column(String)

    password: Mapped[str] = mapped_column(String)

    role: Mapped[str] = mapped_column(String)


    