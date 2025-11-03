import os, logging
from google.cloud import firestore
from google.oauth2 import service_account

logger = logging.getLogger("uvicorn.error")

PROJECT_ID = os.getenv("GCP_PROJECT") or os.getenv("PROJECT_ID") or "asistente-sebastian"
SA_KEY_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or "/secrets/firestore-key.json"

_db = None

def get_db():
    """Singleton de Firestore con ADC o service account file."""
    global _db
    if _db is not None:
        return _db
    creds = None
    try:
        if SA_KEY_PATH and os.path.exists(SA_KEY_PATH):
            creds = service_account.Credentials.from_service_account_file(SA_KEY_PATH)
            logger.info("Firestore usando service account de %s", SA_KEY_PATH)
        else:
            logger.info("Firestore usando Application Default Credentials")
        _db = firestore.Client(project=PROJECT_ID, credentials=creds)
        return _db
    except Exception:
        logger.error("No se pudo inicializar Firestore", exc_info=True)
        raise
