from sqlalchemy import Integer, Column, String, VARCHAR, Text, DATE, FLOAT
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime, date
from sqlalchemy import Float
from database import Base
from pgvector.sqlalchemy import Vector

class Problem_box(Base):
    
    __tablename__ ='problem_box'

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)

    name: Mapped[str] = mapped_column(String)

    role: Mapped[str] = mapped_column(String)

    description: Mapped[str] = mapped_column(String)

    embeddings: Mapped[list[float]] = mapped_column(type_=Vector(384)) 

    status: Mapped[str] = mapped_column(String)
    


    