terraform {
  required_version = ">= 1.3.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Service Account for Agent Execution
resource "google_service_account" "agent_sa" {
  account_id   = "${var.app_name}-sa"
  display_name = "Service Account for ${var.app_name}"
}

# Secret Manager Resource for API Keys
resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "GEMINI_API_KEY"

  replication {
    auto {}
  }
}

# IAM Binding allowing Agent Service Account to access Secret Manager
resource "google_secret_manager_secret_iam_member" "secret_access" {
  secret_id = google_secret_manager_secret.gemini_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agent_sa.email}"
}

# Cloud Run Service for ADK Agent Deployment
resource "google_cloud_run_v2_service" "agent_service" {
  name     = var.app_name
  location = var.region

  template {
    service_account = google_service_account.agent_sa.email

    containers {
      image = "gcr.io/${var.project_id}/${var.app_name}:latest"

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      env {
        name  = "DATABASE_URL"
        value = "sqlite:///sessions.db"
      }
    }
  }
}

# Make Cloud Run Service publicly accessible (or restrict as needed)
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.agent_service.name
  location = google_cloud_run_v2_service.agent_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
