from google.cloud import firestore
from google.auth import default as google_auth_default
import os

_client = None

def _build_client_via_adc():
    # Intenta ADC (SA de Cloud Run) con respeto a QUOTA_PROJECT y PROJECT
    creds, project_id = google_auth_default(quota_project_id=os.getenv("GOOGLE_CLOUD_QUOTA_PROJECT"))
    effective_project = os.getenv("GOOGLE_CLOUD_PROJECT") or project_id
    return firestore.Client(project=effective_project, credentials=creds)

def _build_client_via_env():
    # Si está GOOGLE_APPLICATION_CREDENTIALS, o ADC sin quota project
    return firestore.Client()

def get_client():
    global _client
    if _client is not None:
        return _client
    # 1) ADC con quota project
    try:
        _client = _build_client_via_adc()
        return _client
    except Exception:
        pass
    # 2) Fallback: lo que resuelva google-cloud-firestore (ADC/env var)
    try:
        _client = _build_client_via_env()
        return _client
    except Exception as e:
        raise RuntimeError(f"Firestore client init failed: {e}")

# Alias por compatibilidad retro
def get_firestore_client():
    return get_client()
