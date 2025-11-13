from google.cloud import firestore
import os

_client = None

def get_db():
    """
    Devuelve un cliente Firestore singleton.
    Usa la variable GOOGLE_APPLICATION_CREDENTIALS montada en Cloud Run.
    """
    global _client
    if _client is None:
        _client = firestore.Client()
    return _client
