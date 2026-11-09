from pathlib import Path
import json
import re
import urllib.request
import uuid
from playwright.sync_api import sync_playwright, expect

root = Path(__file__).resolve().parents[1]
out = root/'docs/screenshots'
out.mkdir(exist_ok=True)
plate = 'U'+uuid.uuid4().hex[:8].upper()
errors = []
def call(service, path, method='GET'):
    r = urllib.request.Request(f'http://localhost:8080/api/{service}/{path}', method=method)
    with urllib.request.urlopen(r) as response:
        return json.load(response) if response.status != 204 else None

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width':1440,'height':1050},device_scale_factor=1)
        page.on('pageerror',lambda error: errors.append(str(error)))
        page.goto('http://localhost:8080')
        expect(page.get_by_text('Conectando con los microservicios…')).to_have_count(0)
        page.get_by_role('button',name=re.compile('Vehículos')).click()
        page.get_by_label('Placa',exact=True).fill(plate)
        page.get_by_label('Propietario',exact=True).fill('Prueba visual GlitchTec')
        page.get_by_label('Color',exact=True).fill('Azul')
        page.get_by_role('button',name='Guardar vehículo',exact=True).click()
        row = page.get_by_role('row').filter(has_text=plate)
        expect(row).to_be_visible()
        row.get_by_role('button',name='Editar',exact=True).click()
        page.get_by_label('Color',exact=True).fill('Verde')
        page.get_by_role('button',name='Guardar vehículo',exact=True).click()
        expect(row).to_contain_text('Verde')
        page.get_by_role('button',name=re.compile('Tickets de estadía')).click()
        page.get_by_label('Vehículo',exact=False).select_option(label=f'{plate} · Prueba visual GlitchTec')
        page.get_by_label('Entrada',exact=True).fill('2026-11-09T08:00')
        page.get_by_role('button',name='Guardar ticket',exact=True).click()
        row = page.get_by_role('row').filter(has_text=plate)
        expect(row).to_contain_text('Activo')
        row.get_by_role('button',name='Editar / salida',exact=True).click()
        page.get_by_label(re.compile('Salida')).fill('2026-11-09T09:01')
        page.get_by_role('button',name='Guardar ticket',exact=True).click()
        expect(row).to_contain_text('Cerrado')
        expect(row).to_contain_text('20.00')
        page.screenshot(path=str(out/'local-desktop.png'),full_page=True)
        page.get_by_role('button',name=re.compile('Nuestro equipo')).click()
        for carnet in ['1072123','1185023','1207022','1184523','1304223','1143323']:
            expect(page.get_by_text(carnet,exact=True)).to_be_visible()
        page.screenshot(path=str(out/'local-team.png'),full_page=True)
        page.set_viewport_size({'width':390,'height':844})
        page.get_by_role('button',name=re.compile('Tickets de estadía')).click()
        expect(page.get_by_role('heading',name='Cada estadía, bajo control.')).to_be_visible()
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Desborde horizontal de la página'
        page.screenshot(path=str(out/'local-mobile.png'),full_page=True)
        page.on('dialog',lambda dialog:dialog.accept())
        row = page.get_by_role('row').filter(has_text=plate)
        row.get_by_role('button',name='Eliminar',exact=True).click()
        expect(row).to_have_count(0)
        page.get_by_role('button',name=re.compile('Vehículos')).click()
        row = page.get_by_role('row').filter(has_text=plate)
        row.get_by_role('button',name='Eliminar',exact=True).click()
        expect(row).to_have_count(0)
        assert not errors, errors
        browser.close()
    print('OK UI: CRUD de ambas entidades, seis integrantes, escritorio/móvil sin desborde ni errores JS')
finally:
    for v in call('vehicles','vehicles?limit=1000'):
        if v['plate']==plate:
            for t in call('tickets','tickets?limit=1000'):
                if t['vehicle_id']==v['id']:
                    call('tickets',f"tickets/{t['id']}",'DELETE')
            call('vehicles',f"vehicles/{v['id']}",'DELETE')
