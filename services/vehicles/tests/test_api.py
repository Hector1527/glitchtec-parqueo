import os
from pathlib import Path
import pytest

# Cada suite usa su proceso y su base aislada; no modifica PostgreSQL real.
os.environ["DATABASE_URL"] = "sqlite://"
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.pool import StaticPool
from app.db import Base, get_db
from app import health
from app.main import app
from app.models import Member
from sqlalchemy.orm import Session

@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    @event.listens_for(engine, "connect")
    def foreign_keys(conn, record):
        conn.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(engine)
    with engine.begin() as c:
        c.execute(text("CREATE TABLE tickets (id INTEGER PRIMARY KEY, vehicle_id INTEGER REFERENCES vehicles(id) ON DELETE RESTRICT)"))
    original = health.engine
    health.engine = engine
    def override():
        with Session(engine) as db:
            yield db
    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c, engine
    app.dependency_overrides.clear()
    health.engine = original
    engine.dispose()

DATA = {"plate": "p123abc", "owner": "Hector Pérez", "kind": "Automóvil", "color": "Azul"}

def test_vehicle_crud(client):
    c, _ = client
    r = c.post("/vehicles", json=DATA)
    assert r.status_code == 201
    row = r.json()
    assert row["plate"] == "P123ABC"
    assert c.get(f"/vehicles/{row['id']}").json()["owner"] == DATA["owner"]
    assert len(c.get("/vehicles").json()) == 1
    assert c.put(f"/vehicles/{row['id']}", json={**DATA, "color": "Negro"}).json()["color"] == "Negro"
    assert c.delete(f"/vehicles/{row['id']}").status_code == 204
    assert c.get(f"/vehicles/{row['id']}").status_code == 404

def test_duplicate_plate_and_recovery(client):
    c, _ = client
    assert c.post("/vehicles", json=DATA).status_code == 201
    assert c.post("/vehicles", json=DATA).status_code == 409
    assert c.post("/vehicles", json={**DATA,"plate":"P999XYZ"}).status_code == 201

@pytest.mark.parametrize("patch", [{"plate":"?"},{"owner":"  "},{"kind":"Avión"},{"color":""}])
def test_validation(client, patch):
    assert client[0].post("/vehicles", json={**DATA, **patch}).status_code == 422

def test_vehicle_with_ticket_cannot_be_deleted(client):
    c, engine = client
    vid = c.post("/vehicles", json=DATA).json()["id"]
    with engine.begin() as db:
        db.execute(text("INSERT INTO tickets (vehicle_id) VALUES (:id)"), {"id":vid})
    assert c.delete(f"/vehicles/{vid}").status_code == 409
    assert c.get(f"/vehicles/{vid}").status_code == 200

def test_members_and_health(client):
    c, engine = client
    with Session(engine) as db:
        db.add(Member(student_id="1304223", name="Hector Pérez"))
        db.commit()
    assert c.get("/members").json() == [{"name":"Hector Pérez","student_id":"1304223"}]
    assert c.get("/ready").status_code == 200
    assert c.get("/health").status_code == 200

def test_missing_and_pagination(client):
    c, _ = client
    assert c.delete("/vehicles/999").status_code == 404
    assert c.put("/vehicles/999", json=DATA).status_code == 404
    assert c.get("/vehicles?limit=0").status_code == 422
