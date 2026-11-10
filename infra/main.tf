locals {
  region = join("-", slice(split("-", var.zone), 0, 2))
}
resource "google_project_service" "apis" {
  for_each           = toset(["compute.googleapis.com", "container.googleapis.com", "artifactregistry.googleapis.com", "iam.googleapis.com", "logging.googleapis.com", "monitoring.googleapis.com"])
  service            = each.key
  disable_on_destroy = false
}
resource "google_compute_network" "main" {
  name                    = "${var.cluster_name}-vpc"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.apis]
}
resource "google_compute_subnetwork" "main" {
  name          = "${var.cluster_name}-subnet"
  region        = local.region
  network       = google_compute_network.main.id
  ip_cidr_range = "10.30.0.0/24"
  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.31.0.0/20"
  }
  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.32.0.0/24"
  }
}
resource "google_artifact_registry_repository" "images" {
  location      = local.region
  repository_id = var.repository_id
  description   = "GlitchTec: frontend, vehículos, tickets y PostgreSQL inicializado"
  format        = "DOCKER"
  depends_on    = [google_project_service.apis]
}
resource "google_service_account" "nodes" {
  account_id   = "${var.cluster_name}-nodes"
  display_name = "GlitchTec GKE nodes"
  depends_on   = [google_project_service.apis]
}
resource "google_project_iam_member" "node_roles" {
  for_each = toset(["roles/logging.logWriter", "roles/monitoring.metricWriter", "roles/container.defaultNodeServiceAccount"])
  project  = var.project_id
  role     = each.key
  member   = "serviceAccount:${google_service_account.nodes.email}"
}
resource "google_artifact_registry_repository_iam_member" "pull" {
  location   = google_artifact_registry_repository.images.location
  repository = google_artifact_registry_repository.images.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.nodes.email}"
}
resource "google_container_cluster" "main" {
  name                     = var.cluster_name
  location                 = var.zone
  remove_default_node_pool = true
  initial_node_count       = 1
  deletion_protection      = false
  network                  = google_compute_network.main.id
  subnetwork               = google_compute_subnetwork.main.id
  release_channel { channel = "REGULAR" }
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = var.master_authorized_cidr
      display_name = "operador"
    }
  }
  workload_identity_config { workload_pool = "${var.project_id}.svc.id.goog" }
  logging_service    = "logging.googleapis.com/kubernetes"
  monitoring_service = "monitoring.googleapis.com/kubernetes"
  addons_config {
    gce_persistent_disk_csi_driver_config { enabled = true }
    # Addons que no usamos y que ocupan cupos de pods en los nodos e2-small.
    gcp_filestore_csi_driver_config { enabled = false }
    http_load_balancing { disabled = true }
  }
  monitoring_config {
    managed_prometheus { enabled = false }
  }
  # El pool temporal inicial también respeta e2-small spot. Se elimina antes del pool final.
  node_config {
    machine_type    = "e2-small"
    spot            = true
    disk_size_gb    = 20
    disk_type       = "pd-standard"
    service_account = google_service_account.nodes.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
  }
  depends_on = [google_project_iam_member.node_roles]
}
resource "google_container_node_pool" "spot" {
  name              = "glitchtec-spot"
  location          = var.zone
  cluster           = google_container_cluster.main.name
  node_count        = 2
  max_pods_per_node = 32
  node_config {
    machine_type    = "e2-small"
    spot            = true
    disk_size_gb    = 20
    disk_type       = "pd-standard"
    image_type      = "COS_CONTAINERD"
    service_account = google_service_account.nodes.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
    metadata        = { disable-legacy-endpoints = "true" }
    workload_metadata_config { mode = "GKE_METADATA" }
    labels = { team = "glitchtec" }
  }
  management {
    auto_repair  = true
    auto_upgrade = true
  }
  # Nunca aumentar temporalmente a tres nodos durante una actualización.
  upgrade_settings {
    max_surge       = 0
    max_unavailable = 1
  }
  depends_on = [google_artifact_registry_repository_iam_member.pull]
}
