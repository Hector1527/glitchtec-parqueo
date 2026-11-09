variable "project_id" {
  description = "Proyecto existente con facturación activa."
  type        = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "Indica un ID de proyecto GCP válido."
  }
}
variable "zone" {
  description = "Zona única de GKE y de los dos nodos."
  type        = string
  default     = "us-central1-a"
  validation {
    condition     = can(regex("^[a-z]+-[a-z0-9]+[0-9]-[a-z]$", var.zone))
    error_message = "Usa una zona como us-central1-a."
  }
}
variable "cluster_name" {
  description = "Nombre del clúster; debe identificar al equipo."
  type        = string
  default     = "glitchtec-gke"
  validation {
    condition     = can(regex("^glitchtec(-[a-z0-9-]+)?$", var.cluster_name)) && length(var.cluster_name) <= 24
    error_message = "El nombre debe comenzar con glitchtec y tener máximo 24 caracteres."
  }
}
variable "repository_id" {
  type    = string
  default = "glitchtec"
}
variable "master_authorized_cidr" {
  description = "IP pública del operador /32; habilitar también IPs de otros integrantes si hace falta."
  type        = string
  validation {
    condition     = can(cidrhost(var.master_authorized_cidr, 0)) && !endswith(var.master_authorized_cidr, "/0")
    error_message = "Indica un CIDR restringido válido, preferentemente tu IP/32; no 0.0.0.0/0."
  }
}
