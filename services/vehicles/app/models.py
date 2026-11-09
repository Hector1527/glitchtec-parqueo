from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Vehicle(Base):
    __tablename__ = "vehicles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plate: Mapped[str] = mapped_column(String(12), unique=True)
    owner: Mapped[str] = mapped_column(String(100))
    kind: Mapped[str] = mapped_column(String(20))
    color: Mapped[str] = mapped_column(String(40))

class Member(Base):
    __tablename__ = "members"
    student_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
