"""Prueba HTTP integrada contra Compose/GKE: crea, edita, consulta y elimina sus propios datos."""
import json
import sys
import uuid
import urllib.request
from urllib.error import HTTPError
from datetime import datetime, timedelta, timezone

base = (sys.argv[1] if len(sys.argv)>1 else "http://localhost:8080").rstrip("/")
def request(service, path, method="GET", data=None, expected=200):
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(f"{base}/api/{service}/{path}", data=body, method=method,
                               headers={"Content-Type":"application/json"})
    try:
        response = urllib.request.urlopen(r, timeout=20)
    except HTTPError as e:
        if e.code == expected:
            return None
        raise AssertionError(f"{method} {path}: {e.code} {e.read().decode()}") from e
    with response:
        assert response.status == expected, (path, response.status)
        return json.load(response) if expected != 204 else None

vid = tid = None
try:
    members = request("vehicles", "members")
    assert {m["student_id"] for m in members} == {"1072123","1185023","1207022","1184523","1304223","1143323"}
    v = {"plate": "T"+uuid.uuid4().hex[:10].upper(), "owner":"Prueba integrada", "kind":"Automóvil", "color":"Azul"}
    vid = request("vehicles", "vehicles", "POST", v, 201)["id"]
    assert request("vehicles", f"vehicles/{vid}")["plate"] == v["plate"]
    assert request("vehicles", f"vehicles/{vid}", "PUT", {**v,"color":"Verde"})["color"] == "Verde"
    start = datetime.now(timezone.utc)-timedelta(hours=2)
    t = {"vehicle_id":vid,"entry_at":start.isoformat(),"exit_at":None,"hourly_rate":"10.00"}
    tid = request("tickets", "tickets", "POST", t, 201)["id"]
    request("tickets", "tickets", "POST", t, 409)
    request("vehicles", f"vehicles/{vid}", "DELETE", expected=409)
    assert request("tickets", f"tickets/{tid}")["status"] == "Activo"
    result = request("tickets", f"tickets/{tid}", "PUT", {**t,"exit_at":(start+timedelta(minutes=61)).isoformat()})
    assert result["total"] == "20.00"
    assert any(row["id"]==tid for row in request("tickets","tickets"))
    print("OK: ambos CRUD, FK, unicidad de estadía activa, tarifa y seis integrantes")
finally:
    if tid is not None: request("tickets", f"tickets/{tid}", "DELETE", expected=204)
    if vid is not None: request("vehicles", f"vehicles/{vid}", "DELETE", expected=204)
