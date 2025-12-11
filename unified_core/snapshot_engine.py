from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter
from google.cloud import firestore

from unified_core.context_engine import build_context_bundle

router = APIRouter(prefix="/context", tags=["unified_context"])


def save_snapshot_to_firestore(user_id: str, snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Guarda el snapshot unificado en Firestore.
    """
    try:
        db = firestore.Client()
        doc_ref = (
            db.collection("unified_context_snapshots")
            .document(user_id)
            .collection("snapshots")
            .document()
        )
        doc_ref.set(snapshot)

        return {
            "status": "ok",
            "snapshot_id": doc_ref.id,
            "message": "Snapshot saved to Firestore."
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not save snapshot: {e}"
        }


def generate_snapshot(user_id: str) -> Dict[str, Any]:
    """
    Construye un paquete de contexto unificado.
    """
    bundle = build_context_bundle(user_id=user_id)

    snapshot = {
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "context_bundle": bundle,
        "version": "v7-unified"
    }

    return snapshot


@router.get("/snapshot/manual")
def manual_snapshot(user_id: str = "sebastian"):
    """
    Genera un snapshot manual y lo guarda en Firestore.
    """
    snapshot = generate_snapshot(user_id)
    result = save_snapshot_to_firestore(user_id, snapshot)

    return {
        "snapshot": snapshot,
        "firestore": result
    }
