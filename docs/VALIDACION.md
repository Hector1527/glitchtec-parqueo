# Verificación ejecutada · 9 de noviembre de 2026

Este registro distingue pruebas ejecutadas de tareas todavía pendientes. No afirma
un despliegue en Google Cloud ni aprobación de la rúbrica.

| Comprobación | Resultado observado |
|---|---|
| API vehículos, suite aislada | **9 pruebas aprobadas** |
| API tickets, suite aislada | **10 pruebas aprobadas** |
| Dependencias Python entregadas | Suites repetidas en venv con FastAPI 0.162.2, SQLAlchemy 2.1.8, psycopg 3.3.8 y resto del runtime fijado |
| Aviso del ejecutor de pruebas | Starlette avisa que su integración con httpx está deprecada; las 19 pruebas pasan. Es un aviso de la dependencia de test, no un fallo de petición. |
| React/Vite | `npm run build` correcto con Vite 6.4.6 |
| Dependencias npm | `npm audit`: **0 vulnerabilidades reportadas** tras actualizar Vite |
| Dockerfiles | Construidas las cuatro imágenes: frontend, vehicles, tickets y postgres |
| Docker Compose | Los cuatro servicios alcanzaron estado **healthy**, con PostgreSQL real y volumen persistente |
| HTTP por Nginx | `scripts/smoke.py` aprobó ambos CRUD, FK restrictiva, unicidad de ticket activo, cobro y seis integrantes; limpió sus registros |
| Persistencia local | `scripts/persistence-smoke.py` recreó PostgreSQL con otro ID de contenedor, verificó el mismo vehículo sobre el volumen y eliminó su dato de prueba |
| Navegador Chromium | Crear/editar/consultar/eliminar vehículos y tickets, cerrar estadía y verificar total; ver seis carnés de DB |
| Vista adaptable | Escritorio 1440px y móvil 390px; sin desborde horizontal de la página ni excepciones JavaScript; tablas tienen scroll propio en móvil |
| Capturas reales locales | `docs/screenshots/local-desktop.png`, `local-team.png`, `local-mobile.png`; no equivalen a evidencia GKE |
| Terraform | 1.13.5, `init -backend=false`, proveedor Google 6.50.0; `fmt -check -recursive` y `validate` correctos |
| Kubernetes | Renderizados base, overlay tickets=3 y rollout vehicles=v2 con `kubectl kustomize`; comprobaciones estáticas de cuatro Deployments, imágenes AR, probes, recursos, Services y PVC correctas |

Una prueba detectó inicialmente que SQLite perdía la zona horaria al persistir fechas.
Se normalizaron las entradas a UTC antes de guardar; se repitió la suite y pasó el
caso de entrada -06:00/salida UTC con el mismo instante y cobro mínimo de una hora.

Medición local de referencia en reposo con las dependencias definitivas:
frontend 10.48 MiB, vehículos 64.43 MiB, tickets 62.77 MiB y PostgreSQL 18.68 MiB.
Se ajustaron los requests de las APIs a 80Mi, manteniendo sus límites en 192Mi.
Es una observación puntual de Docker Desktop, no una prueba de carga ni una medición
del clúster. Comprobar recursos reales de GKE antes de la defensa y después de escalar.

El proyecto se copió a `C:\Users\hecto\glitchtec-parqueo`. Desde esa carpeta se
repitieron `docker compose config`, arranque con `--wait`, smoke HTTP y prueba UI;
los cuatro servicios permanecen saludables. Las comprobaciones de sintaxis Python y
PowerShell pasaron, y `.env` quedó excluido del índice Git.

## Pendiente: requiere cuenta, autorización o resultados reales

- Proyecto GCP elegido, permisos, facturación/cuota y alerta de presupuesto.
- Cotización regional final con captura G1 previa al despliegue.
- `terraform plan` con credenciales reales y capturas D3; **no se ejecutó apply/destroy**.
- Crear GKE/Artifact Registry, publicar las cuatro imágenes y comprobar sus digests.
- Validación de esquemas/admisión en servidor Kubernetes y arranque real en GKE.
- Verificación de recursos allocatable y consumo en los dos e2-small Spot.
- IP pública externa, escalamiento 3/3, autorrecuperación, persistencia del PVC y rolling update **en GKE**.
- Repositorio remoto/enlace de entrega, historial auténtico A1 de ≥10 commits en ≥3 días.
- PDF final con capturas oficiales completas A-G; salida real de destroy y gasto final de Billing.

Los scripts de publicación/renderizado/Secret están preparados y comprobados en sus
partes locales. Publicar o desplegar no se presenta como ejecutado. El CI está
versionado; su ejecución en GitHub Actions requiere publicar el repositorio y no ha
sido observada en esta sesión.
