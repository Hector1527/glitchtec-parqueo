output "project_id" { value = var.project_id }
output "cluster_name" { value = google_container_cluster.main.name }
output "zone" { value = var.zone }
output "region" { value = local.region }
output "registry" { value = "${local.region}-docker.pkg.dev/${var.project_id}/${var.repository_id}" }
output "node_service_account" { value = google_service_account.nodes.email }
