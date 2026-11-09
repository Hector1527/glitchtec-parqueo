# Preparación de la defensa individual

El PDF establece 12 minutos de demostración y luego preguntas cruzadas. No permite
leer guiones ni ejecutar scripts preparados para responder preguntas operativas.
Este documento sirve para estudiar con anticipación. Practicar escribiendo comandos
individuales y explicando lo que cambia en Kubernetes, sin depender de scripts.

Cada integrante debe poder:

- Explicar imagen vs contenedor, Deployment vs Pod vs Service, y cómo Nginx resuelve DNS.
- Localizar la entidad que escribe cada API y explicar la FK y el índice de estadía activa.
- Demostrar los cuatro métodos de cada entidad y por qué eliminar un vehículo puede dar 409.
- Explicar UTC, tarifa por fracción y por qué se calcula del lado del servidor con Decimal.
- Encontrar ConfigMap/Secret consumidos sin imprimir la contraseña. Base64 no es cifrado.
- Explicar PVC RWO, montaje PGDATA, Recreate para PostgreSQL y pérdida al borrar el volumen.
- Cambiar réplicas en YAML, aplicar y observar ReplicaSet; diferenciarlo de aumentar nodos.
- Borrar un pod y verificar UID nuevo; explicar que el Deployment reconcilia estado deseado.
- Publicar un tag nuevo y explicar maxSurge/maxUnavailable, readiness y rolling update/rollback.
- Leer logs/eventos y diagnosticar ImagePullBackOff, CrashLoopBackOff, OOMKilled y Pending.
- Explicar Standard zonal, e2-small Spot, preempción, SA de nodos y permiso lector de AR.
- Describir qué maneja Terraform y qué maneja kubectl, el estado privado y orden de destrucción.
- Enumerar costos además de las VM: gestión, discos, LB, IP, imágenes, tráfico y observabilidad.

Repartir la revisión de módulos entre los seis, pero intercambiar preguntas: el docente
elige quién opera. Verificar antes del turno que todos estén presentes, cuenta/proyecto
correctos, clúster activo, datos visibles y capturas completas A-G entregadas.
