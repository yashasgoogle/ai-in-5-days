"""Secure Secret Manager Integration for Google Cloud Secret Manager."""

import os
import logging
from typing import Optional

logger = logging.getLogger("travel_concierge.secrets")


def get_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieves a secret securely from Google Cloud Secret Manager, with environment fallback.

    Args:
        secret_name: The name of the secret (e.g. 'GEMINI_API_KEY', 'OPENWEATHER_API_KEY').
        default: Fallback default value if secret is not set in Secret Manager or env.

    Returns:
        Secret string value or default fallback.
    """
    gcp_project = os.environ.get("GOOGLE_CLOUD_PROJECT")

    # Attempt fetching from GCP Secret Manager if project ID is configured
    if gcp_project:
        try:
            from google.cloud import secretmanager

            client = secretmanager.SecretManagerServiceClient()
            resource_name = f"projects/{gcp_project}/secrets/{secret_name}/versions/latest"
            response = client.access_secret_version(request={"name": resource_name})
            secret_value = response.payload.data.decode("UTF-8").strip()
            logger.info(f"Successfully retrieved secret '{secret_name}' from GCP Secret Manager.")
            return secret_value
        except Exception as err:
            logger.debug(f"GCP Secret Manager lookup for '{secret_name}' failed ({str(err)}). Falling back to environment variable.")

    # Fallback to local environment variable
    env_value = os.environ.get(secret_name)
    if env_value:
        return env_value

    return default
