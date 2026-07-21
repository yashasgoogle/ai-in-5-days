output "service_account_email" {
  value       = google_service_account.agent_sa.email
  description = "The email of the created agent service account."
}

output "cloud_run_url" {
  value       = google_cloud_run_v2_service.agent_service.uri
  description = "The public URL of the deployed agent service."
}

output "secret_id" {
  value       = google_secret_manager_secret.gemini_api_key.secret_id
  description = "The ID of the Secret Manager secret for API keys."
}
