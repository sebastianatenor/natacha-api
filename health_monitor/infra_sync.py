import os
from datetime import datetime
from typing import Any, Dict, List, Optional

# Fallbacks de import locales (no recursivos)
try:
    from .infra_local_history import clear_history, get_history
except Exception:
    from infra_local_history import clear_history, get_history

try:
    from google.cloud import firestore
except Exception:
    firestore = (
        None  # permitirá importar el módulo sin la lib; fallará al usar Firestore
    )


# -----------------------------
# Config
# -----------------------------
GCP_PROJECT: Optional[str] = (
    os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT") or None
)
COLL_NAME = os.getenv("INFRA_HISTORY_COLLECTION", "infra_history")


# -----------------------------
# Firestore Client
# -----------------------------
def get_firestore_client():
    """
    Devuelve un cliente de Firestore.
    Requiere 'google-cloud-firestore' instalado y credenciales válidas (ADC).
    """
    if firestore is None:
        raise RuntimeError("google-cloud-firestore no está disponible en el entorno.")
    if GCP_PROJECT:
        return firestore.Client(project=GCP_PROJECT)
    return firestore.Client()


# -----------------------------
# Push unitario a Firestore
# -----------------------------
def push_to_firestore(entry: Dict[str, Any]) -> str:
    """
    Inserta un documento en la colección COLL_NAME y devuelve el id asignado.
    """
    db = get_firestore_client()
    data = dict(entry) if isinstance(entry, dict) else {"entry": entry}
    # sello temporal
    data.setdefault("created_at", datetime.utcnow().isoformat() + "Z")
    ref = db.collection(COLL_NAME).add(data)[1]
    return ref.id


# -----------------------------
# Sincronización local -> Firestore
# -----------------------------
def sync_local_to_firestore() -> Dict[str, Any]:
    """
    Lee el historial local (infra_local_history.get_history) y lo sube a Firestore.
    Si sube al menos 1, limpia el historial local.
    """
    try:
        hist: List[Dict[str, Any]] = get_history() or []
    except Exception as e:
        return {"status": "error", "detail": f"Error leyendo historial local: {e}"}

    if not hist:
        return {"status": "ok", "pushed": 0, "message": "Historial local vacío"}

    pushed, errors, last_error = 0, 0, None
    for item in hist:
        try:
            push_to_firestore(item)
            pushed += 1
        except Exception as e:
            errors += 1
            last_error = str(e)

    # si se subió algo, limpiamos el historial local
    if pushed and errors == 0:
        try:
            clear_history()
        except Exception:
            # no consideramos esto un error fatal de sync
            pass

    out: Dict[str, Any] = {
        "status": "ok" if errors == 0 else "partial",
        "pushed": pushed,
        "errors": errors,
    }
    if last_error:
        out["last_error"] = last_error
    return out


# -----------------------------
# Lectura desde Firestore
# -----------------------------
def pull_from_firestore(limit: int = 20) -> Dict[str, Any]:
    """
    Devuelve hasta 'limit' registros desde Firestore, más recientes primero.
    Intenta ordenar por 'created_at'; si no existe, ordena por id desc.
    """
    try:
        db = get_firestore_client()
        coll = db.collection(COLL_NAME)

        try:
            # si los docs tienen created_at
            qry = coll.order_by(
                "created_at", direction=firestore.Query.DESCENDING
            ).limit(limit)
            docs = list(qry.stream())
        except Exception:
            # fallback: orden por nombre de doc (id) desc
            qry = coll.order_by("__name__", direction=firestore.Query.DESCENDING).limit(
                limit
            )
            docs = list(qry.stream())

        out = []
        for d in docs:
            obj = d.to_dict() or {}
            obj["_id"] = d.id
            out.append(obj)

        return {"status": "ok", "count": len(out), "data": out}

    except Exception as e:
        return {"status": "error", "detail": str(e)}
