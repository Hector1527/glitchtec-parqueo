"""Recrea SOLO el contenedor PostgreSQL de Compose y comprueba que conserva un vehículo."""
import json
from pathlib import Path
import subprocess
import urllib.request
import uuid

root = Path(__file__).resolve().parents[1]
base = 'http://localhost:8080/api/vehicles/vehicles'
def request(url, method='GET', data=None):
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method, headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=20) as r:
        return json.load(r) if r.status != 204 else None

vid = None
try:
    data = {'plate':'D'+uuid.uuid4().hex[:9].upper(),'owner':'Prueba de persistencia','kind':'Otro','color':'Verde'}
    vid = request(base,'POST',data)['id']
    old = subprocess.check_output(['docker','compose','ps','-q','postgres'],cwd=root,text=True).strip()
    subprocess.check_call(['docker','compose','up','-d','--no-deps','--force-recreate','--wait','--wait-timeout','120','postgres'],cwd=root)
    new = subprocess.check_output(['docker','compose','ps','-q','postgres'],cwd=root,text=True).strip()
    assert old != new and old and new
    assert request(f'{base}/{vid}')['plate'] == data['plate']
    print(f'OK persistencia local: contenedor {old[:12]} -> {new[:12]}, vehículo conservado sobre el mismo volumen')
finally:
    if vid is not None:
        request(f'{base}/{vid}','DELETE')
