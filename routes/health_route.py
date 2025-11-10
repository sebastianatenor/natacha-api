from fastapi import APIRouter
import os
import inspect
import hashlib

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/health/deps")
def health_deps():
    """
    Chequeos no destructivos:
    - Import y cliente de Firestore (en runtime, con try/except)
    - Lectura mínima (limit=1) protegida
    - Exposición de env no sensibles
    """
    deps = {}

    # Firestore: import perezoso
    try:
        from google.cloud import firestore  # type: ignore
        deps["firestore_import"] = True
    except Exception as e:
        firestore = None  # type: ignore[assignment]
        deps["firestore_import"] = False
        deps["firestore_import_error"] = str(e)

    client_ok = False
    read_ok = False

    if deps.get("firestore_import"):
        try:
            db = firestore.Client()  # type: ignore[name-defined]
            client_ok = True
            try:
                next(db.collection("assistant_memory").limit(1).stream(), None)
                read_ok = True
            except Exception as e:
                deps["firestore_read_error"] = str(e)
        except Exception as e:
            deps["firestore_client_error"] = str(e)

    deps["firestore_client_ok"] = client_ok
    deps["firestore_read_ok"] = read_ok

    env_keys = ["GCP_PROJECT", "GOOGLE_CLOUD_PROJECT", "MEMORY_FILE"]
    deps["env"] = {k: os.getenv(k) for k in env_keys if os.getenv(k)}

    status = "ok" if (deps.get("firestore_import") and client_ok) else "degraded"
    return {"status": status, "deps": deps}

@router.get("/health/debug_source")
def health_debug_source():
    """Ruta del archivo en runtime y SHA256 del módulo."""
    this_file = inspect.getsourcefile(health_debug_source) or "<unknown>"
    with open(__file__, "rb") as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
    return {"file_runtime": this_file, "sha256_this_module": sha}
