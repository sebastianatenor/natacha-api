import json
import os

from google.cloud import firestore
from google.oauth2 import service_account

PROJECT_ID = (
    os.getenv("GOOGLE_CLOUD_PROJECT")
    or os.getenv("GCP_PROJECT")
    or "asistente-sebastian"
)


def get_client():
    """
    Devuelve un cliente de Firestore aun si GOOGLE_APPLICATION_CREDENTIALS
    viene como JSON (caso Cloud Run con --set-secrets=...).
    """
    raw = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # 1) Caso Cloud Run: viene el JSON entero en la variable
    if raw and raw.strip().startswith("{"):
        data = json.loads(raw)
        creds = service_account.Credentials.from_service_account_info(data)
        return firestore.Client(project=PROJECT_ID, credentials=creds)

    # 2) Caso clásico: viene la ruta a un archivo en el contenedor
    if raw and os.path.exists(raw):
        creds = service_account.Credentials.from_service_account_file(raw)
        return firestore.Client(project=PROJECT_ID, credentials=creds)

    # 3) Último recurso: Application Default Credentials (si el runtime las tiene)
    return firestore.Client(project=PROJECT_ID)
