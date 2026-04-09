from sqlalchemy import Integer, Column, String, VARCHAR, Text, DATE, FLOAT
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime, date
from sqlalchemy import Float
from database import Base

class Events(Base):
    __tablename__ ='events'

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)

    name: Mapped[str] = mapped_column(String)

    description: Mapped[str] = mapped_column(String)

    reg_forms: Mapped[str] = mapped_column(String)

    lst_reg_date: Mapped[datetime] = mapped_column(DATE)

    domain: Mapped[str] = mapped_column(String)

    reg_fees: Mapped[float] = mapped_column(FLOAT,default=0.0)

    cont_name: Mapped[str] = mapped_column(String)

    cont_no: Mapped[int] = mapped_column()

    condc_by: Mapped[str] = mapped_column(String)

    venue: Mapped[str] = mapped_column(String)

    start_date: Mapped[date] = mapped_column(DATE)

    end_date: Mapped[datetime] = mapped_column(DATE)






