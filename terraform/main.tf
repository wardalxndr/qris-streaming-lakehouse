terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

variable "project_id" {
  description = "GCP project id milikmu (jangan hardcode di file lain, pakai -var)"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Dataset lakehouse. Tabel mart di dalamnya dikelola dbt (bukan Terraform),
# biar tidak rebutan ownership.
resource "google_bigquery_dataset" "qris_analytics" {
  dataset_id  = "qris_analytics"
  location    = "US"
  description = "QRIS streaming lakehouse: silver source + dbt gold marts"
}

output "dataset" {
  value = google_bigquery_dataset.qris_analytics.dataset_id
}
