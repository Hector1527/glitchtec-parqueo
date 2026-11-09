from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

# Solo id de la entidad externa: este servicio nunca escribe vehículos.
class VehicleReference(Base):
    __tablename__ = "vehicles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        CheckConstraint("hourly_rate > 0", name="positive_rate"),
        CheckConstraint("exit_at IS NULL OR exit_at >= entry_at", name="valid_dates"),
        Index("one_active_ticket_per_vehicle", "vehicle_id", unique=True,
              postgresql_where=text("exit_at IS NULL"), sqlite_where=text("exit_at IS NULL")),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="RESTRICT"), index=True)
    entry_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    exit_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(8, 2))
