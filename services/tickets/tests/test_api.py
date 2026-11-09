import os
import pytest
os.environ["DATABASE_URL"] = "sqlite://"
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.db import Base, get_db
from app import health
from app.main import app
from app.models import VehicleReference

@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread":False}, poolclass=StaticPool)
    @event.listens_for(engine, "connect")
    def foreign_keys(conn, record):
        conn.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(engine)
    with engine.begin() as c:
        c.execute(text("CREATE TABLE members (student_id TEXT PRIMARY KEY, name TEXT)"))
        c.execute(text("INSERT INTO vehicles (id) VALUES (1), (2)"))
    original = health.engine
    health.engine = engine
    def override():
        with Session(engine) as db:
            yield db
    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    health.engine = original
    engine.dispose()

DATA = {"vehicle_id":1,"entry_at":"2026-11-09T12:00:00Z","exit_at":None,"hourly_rate":"10.00"}

def test_ticket_crud_and_rounding(client):
    r = client.post("/tickets", json=DATA)
    assert r.status_code == 201
    row = r.json()
    assert row["status"] == "Activo" and row["total"] is None
    assert len(client.get("/tickets").json()) == 1
    assert client.get(f"/tickets/{row['id']}").status_code == 200
    r = client.put(f"/tickets/{row['id']}", json={**DATA,"exit_at":"2026-11-09T13:01:00Z"})
    assert r.status_code == 200
    assert r.json()["total"] == "20.00" and r.json()["status"] == "Cerrado"
    assert client.delete(f"/tickets/{row['id']}").status_code == 204
    assert client.get(f"/tickets/{row['id']}").status_code == 404

def test_only_one_active_ticket(client):
    assert client.post("/tickets", json=DATA).status_code == 201
    assert client.post("/tickets", json=DATA).status_code == 409
    assert client.post("/tickets", json={**DATA,"vehicle_id":2}).status_code == 201

def test_missing_vehicle(client):
    assert client.post("/tickets", json={**DATA,"vehicle_id":999}).status_code == 422

@pytest.mark.parametrize("patch", [{"hourly_rate":"0"},{"hourly_rate":"-1"},
 {"hourly_rate":"10.123"},{"exit_at":"2026-11-09T11:00:00Z"},{"entry_at":"2026-11-09T12:00:00"}])
def test_validation(client, patch):
    assert client.post("/tickets", json={**DATA,**patch}).status_code == 422

def test_minimum_and_timezone(client):
    r = client.post("/tickets", json={**DATA,"entry_at":"2026-11-09T06:00:00-06:00","exit_at":"2026-11-09T12:00:00Z"})
    assert r.status_code == 201 and r.json()["total"] == "10.00"
    assert client.post("/tickets", json=DATA).status_code == 201

def test_missing_and_health(client):
    assert client.put("/tickets/999", json=DATA).status_code == 404
    assert client.delete("/tickets/999").status_code == 404
    assert client.get("/tickets?offset=-1").status_code == 422
    assert client.get("/ready").status_code == 200
    assert client.get("/health").status_code == 200
