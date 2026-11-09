# Estimación de costos previa al despliegue · GlitchTec

Preparada el **9 de noviembre de 2026** para el diseño de Terraform; **no es gasto
real ni cotización garantizada**. Región de ejemplo us-central1, zona us-central1-a,
730 horas/mes, USD, tráfico ligero de demostración. Sustituir los supuestos por
cotización vigente de la calculadora de Google Cloud ANTES de crear recursos y guardar
captura con reloj/proyecto para G1. El documento registra el presupuesto de diseño;
no afirma haber consultado precios Spot de una cuenta o haber desplegado.

| Recurso declarado/utilizado | Cálculo mensual | Supuesto ilustrativo USD |
|---|---|---:|
| GKE Standard, un control plane zonal | 730 × 0.10/h | 73.00 antes de créditos |
| Dos e2-small Spot | 2 × 730 × 0.004/h (supuesto; variable) | 5.84 |
| Discos de arranque pd-standard, 2 × 20 GiB | 40 × 0.04/GiB-mes (supuesto regional) | 1.60 |
| PVC standard-rwo / pd-balanced de 1 GiB | 1 × 0.10/GiB-mes (supuesto) | 0.10 |
| IPv4 externas de dos nodos Spot | 2 × 730 × 0.0025/h (supuesto) | 3.65 |
| LoadBalancer de red: regla de forwarding | 730 × 0.025/h (supuesto) | 18.25 |
| IP externa del LoadBalancer y procesamiento | confirmar SKU; provisión conservadora | 4.00 |
| Artifact Registry | 1 GiB × 0.10/GiB-mes antes de free tier (supuesto) | 0.10 |
| Logs, métricas y egreso ligero | margen ilustrativo; depende de uso | 2.00 |
| **Total ilustrativo bruto** | suma anterior | **108.54 / mes** |
| **Si aplica crédito de administración GKE al clúster zonal** | restar 73.00 | **35.54 / mes** |

El crédito gratuito de administración GKE se asigna por cuenta de facturación y puede
estar consumido por otro clúster. No asumir que cubre nodos, discos, LB, IPs ni egreso.
Las tarifas marcadas como supuesto **no se presentan como precios verificados**. El
LoadBalancer/IP puede tener tratamiento combinado y debe verificarse para evitar
duplicar o subestimar su cobro. Spot cambia por zona y disponibilidad. No hay NAT,
Ingress adicional, Cloud SQL, dominio ni TLS de pago en esta infraestructura.

Con estos supuestos, una sesión de 8 horas, prorrateando los conceptos horarios y
almacenamiento, rondaría **USD 1.19 brutos** o **USD 0.39 con crédito de gestión GKE**,
más tráfico real, retención de imágenes y variaciones de SKU. Es una aproximación,
no un límite. Dejar el clúster todo el mes cuesta mucho más que una sesión.

Fuentes oficiales para actualizar antes de desplegar:

- [GKE: administración y crédito gratuito](https://cloud.google.com/kubernetes-engine/pricing)
- [Compute Engine: máquinas y Spot](https://cloud.google.com/compute/all-pricing)
- [Discos persistentes](https://cloud.google.com/compute/disks-image-pricing)
- [IP externas y red](https://cloud.google.com/vpc/network-pricing)
- [Cloud Load Balancing](https://cloud.google.com/vpc/network-pricing#lb)
- [Artifact Registry](https://cloud.google.com/artifact-registry/pricing)
- [Calculadora oficial](https://cloud.google.com/products/calculator)

## Cotización del equipo (completar antes de apply)

- Fecha/hora y zona: **PENDIENTE**.
- Proyecto y región confirmados: **PENDIENTE**.
- Precio e2-small Spot por hora consultado: **PENDIENTE**.
- Crédito GKE disponible para esta cuenta: **PENDIENTE**.
- Total mensual de calculadora y captura G1: **PENDIENTE**.
- Presupuesto/alertas configurados y responsable: **PENDIENTE**.
- Fecha/hora prevista para destrucción: inmediatamente después de defensa, confirmar turno.
- Gasto final real en Billing (G3): **PENDIENTE**.

Después de destruir, revisar discos/PVs, LoadBalancers, IPs, repositorio e imágenes;
eliminar un clúster no garantiza limpiar recursos creados fuera de Terraform. No
dejar snapshots o respaldos en la nube sin incluirlos en el presupuesto.
