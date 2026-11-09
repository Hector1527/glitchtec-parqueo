terraform {
  required_version = ">= 1.8, < 2.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}
provider "google" {
  project = var.project_id
  region  = local.region
  zone    = var.zone
}
