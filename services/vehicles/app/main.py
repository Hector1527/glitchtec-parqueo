import re
from typing import Literal
from fastapi import Depends, FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .db import get_db
from .health import lifespan, router
from .models import Member, Vehicle

app = FastAPI(title="GlitchTec · Vehículos", lifespan=lifespan)
app.include_router(router)

class VehicleInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    plate: str = Field(min_length=3, max_length=12)
    owner: str = Field(min_length=1, max_length=100)
    kind: Literal["Automóvil", "Motocicleta", "Pickup", "Otro"] = "Automóvil"
    color: str = Field(min_length=1, max_length=40)

    @field_validator("plate")
    @classmethod
    def valid_plate(cls, value):
        value = value.upper()
        if not re.fullmatch(r"[A-Z0-9-]{3,12}", value):
            raise ValueError("Placa: usar entre 3 y 12 letras, números o guiones")
        return value

class VehicleOutput(VehicleInput):
    model_config = ConfigDict(from_attributes=True)
    id: int

class MemberOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    student_id: str

def find(db, vehicle_id):
    row = db.get(Vehicle, vehicle_id)
    if row is None:
        raise HTTPException(404, "Vehículo no encontrado")
    return row

def commit(db):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Placa duplicada o vehículo con tickets vinculados") from None

@app.get("/members", response_model=list[MemberOutput])
def members(db: Session = Depends(get_db)):
    return db.scalars(select(Member).order_by(Member.student_id)).all()

@app.get("/vehicles", response_model=list[VehicleOutput])
def list_vehicles(limit: int = Query(200, ge=1, le=1000), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    return db.scalars(select(Vehicle).order_by(Vehicle.id.desc()).offset(offset).limit(limit)).all()

@app.post("/vehicles", response_model=VehicleOutput, status_code=201)
def create_vehicle(data: VehicleInput, db: Session = Depends(get_db)):
    row = Vehicle(**data.model_dump())
    db.add(row)
    commit(db)
    db.refresh(row)
    return row

@app.get("/vehicles/{vehicle_id}", response_model=VehicleOutput)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    return find(db, vehicle_id)

@app.put("/vehicles/{vehicle_id}", response_model=VehicleOutput)
def update_vehicle(vehicle_id: int, data: VehicleInput, db: Session = Depends(get_db)):
    row = find(db, vehicle_id)
    for key, value in data.model_dump().items():
        setattr(row, key, value)
    commit(db)
    db.refresh(row)
    return row

@app.delete("/vehicles/{vehicle_id}", status_code=204)
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    db.delete(find(db, vehicle_id))
    commit(db)
    return Response(status_code=204)
