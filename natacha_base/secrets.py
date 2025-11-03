import os

from google.cloud import secretmanager


class SecretManager:
    """
    Wrapper unificado para acceder a secretos de Google Cloud.
    """

    def __init__(self):
        self.client = secretmanager.SecretManagerServiceClient()

    def get_secret(self, name: str, project_id: str = None):
        project = project_id or os.getenv("GCP_PROJECT")
        if not project:
            raise ValueError("GCP_PROJECT environment variable not set.")
        secret_path = f"projects/{project}/secrets/{name}/versions/latest"
        response = self.client.access_secret_version(name=secret_path)
        return response.payload.data.decode("utf-8")
