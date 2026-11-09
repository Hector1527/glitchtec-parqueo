from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING
from fastapi import Depends, FastAPI, HTTPException, Query, Response
from pydantic import AwareDatetime, BaseModel, Field, field_validator, model_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .db import get_db
from .health import lifespan, router
from .models import Ticket, VehicleReference

app = FastAPI(title="GlitchTec · Tickets de estadía", lifespan=lifespan)
app.include_router(router)

class TicketInput(BaseModel):
    vehicle_id: int = Field(gt=0)
    entry_at: AwareDatetime
    exit_at: AwareDatetime | None = None
    hourly_rate: Decimal = Field(gt=0, le=999999, max_digits=8, decimal_places=2)

    @field_validator("entry_at", "exit_at")
    @classmethod
    def normalize_utc(cls, value):
        return value.astimezone(timezone.utc) if value else None

    @model_validator(mode="after")
    def valid_dates(self):
        if self.exit_at and self.exit_at < self.entry_at:
            raise ValueError("La salida no puede preceder a la entrada")
        return self

class TicketOutput(BaseModel):
    id: int
    vehicle_id: int
    entry_at: datetime
    exit_at: datetime | None
    hourly_rate: Decimal
    total: Decimal | None
    status: str

def utc(value):
    return value.replace(tzinfo=timezone.utc) if value and value.tzinfo is None else value

def output(row):
    entry, exit = utc(row.entry_at), utc(row.exit_at)
    total = None
    if exit:
        hours = max(Decimal(1), (Decimal(str((exit-entry).total_seconds())) / 3600).to_integral_value(rounding=ROUND_CEILING))
        total = (hours * row.hourly_rate).quantize(Decimal("0.01"))
    return TicketOutput(id=row.id, vehicle_id=row.vehicle_id, entry_at=entry, exit_at=exit,
                        hourly_rate=row.hourly_rate, total=total, status="Cerrado" if exit else "Activo")

def find(db, ticket_id):
    row = db.get(Ticket, ticket_id)
    if row is None:
        raise HTTPException(404, "Ticket no encontrado")
    return row

def save(db, row, data):
    if db.get(VehicleReference, data.vehicle_id) is None:
        raise HTTPException(422, "El vehículo no existe")
    for key, value in data.model_dump().items():
        setattr(row, key, value)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "El vehículo ya tiene un ticket activo o fue eliminado") from None
    db.refresh(row)
    return output(row)

@app.get("/tickets", response_model=list[TicketOutput])
def list_tickets(limit: int = Query(200, ge=1, le=1000), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    return [output(row) for row in db.scalars(select(Ticket).order_by(Ticket.id.desc()).offset(offset).limit(limit)).all()]

@app.post("/tickets", response_model=TicketOutput, status_code=201)
def create_ticket(data: TicketInput, db: Session = Depends(get_db)):
    return save(db, Ticket(), data)

@app.get("/tickets/{ticket_id}", response_model=TicketOutput)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    return output(find(db, ticket_id))

@app.put("/tickets/{ticket_id}", response_model=TicketOutput)
def update_ticket(ticket_id: int, data: TicketInput, db: Session = Depends(get_db)):
    return save(db, find(db, ticket_id), data)

@app.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    db.delete(find(db, ticket_id))
    db.commit()
    return Response(status_code=204)
