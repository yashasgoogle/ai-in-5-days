variable "project_id" {
  type        = string
  description = "Google Cloud Project ID"
  default     = "ai-in-5-days-project"
}

variable "region" {
  type        = string
  description = "Google Cloud Region for deployment"
  default     = "us-central1"
}

variable "app_name" {
  type        = string
  description = "Application name"
  default     = "travel-concierge-agent"
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev, staging, prod)"
  default     = "production"
}
