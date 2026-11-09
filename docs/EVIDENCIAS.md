# Anexo B · Evidencias GlitchTec

Transcripción operativa de los criterios del PDF oficial, páginas 7-8. **100 puntos =
5 puntos grupales**; los 3 puntos individuales dependen de la defensa. Las casillas
empiezan vacías: existencia de código no significa evidencia obtenida en la nube.
No generar capturas simuladas ni fechas/commits retroactivos.

Antes de cada captura, dejar visibles `Get-Date`, `gcloud config list` y el reloj del
sistema. Para capturas del navegador, organizar ventanas de modo que estos elementos
también se vean. No mostrar secretos, `.env`, claves ni datos privados. Guardar archivos
con nombres A1-..., B1-..., en orden, y exportar un PDF final con el diagrama del README.

| Hecho | Código | Pts | Criterio exacto a demostrar | Evidencia y referencia |
|---|---|---:|---|---|
| [ ] | A1 | 4 | Repositorio con código/manifiestos/.tf, ≥10 commits distribuidos en 3 días distintos | URL Git + `git log --date=iso --pretty=fuller`; historial auténtico. Pendiente si se inicia hoy. |
| [ ] | A2 | 3 | README con caso, integrantes/carné e instrucciones de despliegue | README visible en repositorio remoto. |
| [ ] | A3 | 3 | Diagrama propio con frontend, microservicios, DB y entrada pública | Mermaid del README renderizado, también dentro del PDF. |
| [ ] | A4 | 2 | Carné de cada integrante en DB y visible en UI | `SELECT * FROM members;` y pestaña Nuestro equipo con los seis. |
| [ ] | A5 | 2 | Clúster y namespace identifican al equipo | `gcloud container clusters list`; `kubectl get namespace glitchtec`. |
| [ ] | B1 | 5 | Microservicio A: crear, consultar, actualizar y eliminar | Crear vehículo único, consultarlo, editar color, eliminarlo sin tickets; UI y respuestas HTTP. |
| [ ] | B2 | 5 | Microservicio B: crear, consultar, actualizar y eliminar | Vehículo previo, crear ticket, consultar, editar salida/tarifa, eliminar. |
| [ ] | B3 | 3 | Contenedor independiente y Dockerfile por microservicio | `services/vehicles/Dockerfile`, `services/tickets/Dockerfile`; build y listado de imágenes. |
| [ ] | B4 | 5 | Frontend opera contra ambas APIs y muestra datos de ambas | UI con vehículos y tickets, Network con respuestas reales. |
| [ ] | C1 | 4 | Etiquetas completas Artifact Registry de frontend y ambas APIs | `docker image ls` con rutas completas y tags v1. |
| [ ] | C2 | 3 | Tres imágenes publicadas y listado del repositorio | `gcloud artifacts docker images list $Registry --include-tags` (también debe estar postgres). |
| [ ] | C3 | 3 | Manifiestos usan únicamente imágenes de Artifact Registry | YAML renderizado y `kubectl -n glitchtec get deployments -o yaml`; cuatro rutas AR. |
| [ ] | D1 | 5 | .tf versionados declaran GKE, pool y Artifact Registry | `infra/main.tf` en Git y recursos en estado después del apply. |
| [ ] | D2 | 4 | Variables de proyecto/zona/clúster, sin sensibles en código | `infra/variables.tf`, `.tfvars.example`, `.gitignore`. No capturar tfvars privado. |
| [ ] | D3 | 3 | Salida de terraform plan previa a crear | Captura original ANTES de apply; guardar fecha. |
| [ ] | D4 | 3 | Salida de terraform apply con recursos creados | Captura del apply exitoso y outputs no sensibles. |
| [ ] | D5 | 3 | Node pool de nodos Spot según código | `gcloud container node-pools describe ...` con machineType=e2-small, spot=true y node_count=2. |
| [ ] | E1 | 5 | Todos como Deployments Running | `kubectl -n glitchtec get all`: frontend, vehicles, tickets, postgres. |
| [ ] | E2 | 3 | ConfigMap inyectado y consumido dentro de pod | `get configmap parking-config -o yaml`; `exec deployment/vehicles -- printenv DB_HOST POSTGRES_DB APP_VERSION`. |
| [ ] | E3 | 3 | Secret inyectado y consumido dentro de pod | `describe secret parking-secret` (sin valores) y prueba booleana de variable desde Python en el pod. |
| [ ] | E4 | 5 | PVC montado y datos preservados al borrar pod DB | SELECT de placa real, PVC Bound, UID anterior, borrar pod postgres, nuevo UID, SELECT idéntico. No borrar PVC. |
| [ ] | E5 | 4 | IP pública accesible en navegador externo | `get svc frontend` con EXTERNAL-IP + navegador externo con esa dirección y datos. |
| [ ] | E6 | 2 | Tráfico entre frontend y APIs por DNS Services | Config Nginx + nslookup vehicles/tickets desde frontend + petición funcional. |
| [ ] | F1 | 3 | Escalar microservicio a 3 réplicas declarativamente | `scale3.yaml`, apply, Deployment READY 3/3 y tres pods Running. No usar solo kubectl scale. |
| [ ] | F2 | 2 | Eliminar pod y Deployment lo recrea | UID/nombre anterior, delete pod, UID/nombre nuevo y Running. |
| [ ] | F3 | 3 | Cambiar versión de imagen y mostrar rolling update | v1→v2, YAML, rollout status, ReplicaSets e historial; `/health` version=v2. |
| [ ] | F4 | 2 | Obtener logs de un pod de aplicación | `kubectl -n glitchtec logs deployment/vehicles --tail=100 --timestamps`. |
| [ ] | G1 | 3 | Estimación mensual elaborada antes del despliegue | Completar COSTOS.md con cotización de región/fecha y captura de calculadora ANTES de apply. |
| [ ] | G2 | 3 | Terraform destroy y salida de recursos eliminados | Captura real de destroy, state vacío y consultas de remanentes. Limpiar antes LB/PVC/imágenes. |
| [ ] | G3 | 2 | Panel Billing con gasto final | Captura de costos del proyecto, esperar actualización de facturación. |

Subtotales: **A=14, B=18, C=10, D=18, E=22, F=10, G=8. Total=100**.

## Montaje del archivo de evidencias (pendiente de capturas reales)

1. Portada: GlitchTec, Caso 3, integrantes/carnés, proyecto GCP, zona, enlace Git y fecha.
2. Diagrama propio renderizado desde el README.
3. Secciones A-G en orden. Cada captura rotulada con código, acción y resultado observable.
4. Declarar cualquier criterio no demostrado. No reemplazar una captura faltante por salida inventada.
5. Exportar a PDF y revisar legibilidad de cada captura al 100%; mantener reloj/proyecto visibles.
6. Entregar enlace y PDF antes de 10/11/2026 17:59; añadir evidencia de cierre antes de 13/11 23:59.

El PDF final de evidencia GCP todavía no puede completarse sin ejecutar el despliegue,
la operación y el cierre autorizados. Este checklist no afirma que los criterios hayan sido aprobados.
