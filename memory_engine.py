from datetime import datetime
from typing import Optional, List, Dict, Any

from google.cloud import firestore

db = firestore.Client()

# Colecciones base
COL_RAW = "memory_raw"
COL_SUMMARY = "memory_clean"
COL_SYSTEM = "memory_system"


def _utc_iso() -> str:
    """ISO8601 en UTC."""
    return datetime.utcnow().isoformat()

# Auto-tagging simple basado en palabras clave
AUTO_TAGS = {
    "sophie": "Sophie",
    "jamin": "Jamin",
    "xcmg": "XCMG",
    "grúa": "Cranes",
    "grua": "Cranes",
    "crane": "Cranes",
    "salta": "Salta",
    "buenos aires": "BuenosAires",
    "mercado": "MercadoLibre",
    "importación": "Importaciones",
    "importacion": "Importaciones",
    "china": "China",
    "llvc": "LLVC",
}

def detect_auto_tags(text: str) -> List[str]:
    """
    Detecta tags automáticamente a partir de palabras clave.
    No rompe nada: solo complementa los tags explícitos.
    """
    text_low = text.lower()
    found = []

    for key, tag in AUTO_TAGS.items():
        if key in text_low:
            found.append(tag)

    return found

def save_raw_memory(payload: Dict[str, Any]) -> str:
    """
    Guarda una memoria cruda, pero normalizando algunos campos
    para que sean más fáciles de usar después.
    """
    # Campos "canónicos"
    user_id = payload.get("user_id", "unknown")
    note = payload.get("note", "")
    kind = payload.get("kind", "generic")
    importance = payload.get("importance", "normal")
    source = payload.get("source", "actions")
    tags = payload.get("tags", [])
    auto = detect_auto_tags(note)
    tags = list(set(tags + auto))

    if isinstance(tags, str):
        # Si viene como string "a,b,c" lo pasamos a lista
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    doc_ref = db.collection(COL_RAW).document()

    data = {
        "user_id": user_id,
        "note": note,
        "kind": kind,
        "importance": importance,
        "source": source,
        "tags": tags,
        "created_at": _utc_iso(),
        # Guardamos el payload original por las dudas
        "raw": payload,
    }

    doc_ref.set(data)
    return doc_ref.id


def consolidate_memory(user_id: Optional[str] = None):
    """
    Toma memorias crudas y genera una versión limpia / fusionada.
    Si se pasa user_id consolida solo las de ese usuario,
    si no, consolida todo y guarda en el documento "global".
    """
    # Evitamos combinaciones where+order_by que pueden requerir índices compuestos
    q = db.collection(COL_RAW)

    if user_id:
        q = q.where("user_id", "==", user_id)

    docs = list(q.stream())
    if not docs:
        return None

    notes: List[str] = []
    for d in docs:
        doc_data = d.to_dict() or {}
        n = doc_data.get("note")
        if n:
            notes.append(n)

    if not notes:
        return None

    text = "\n".join(notes)

    key = user_id or "global"
    summary_doc = {
        "user_id": key,
        "summary": text,
        "updated_at": _utc_iso(),
        "count": len(notes),
    }

    db.collection(COL_SUMMARY).document(key).set(summary_doc)
    print(f"[memory_engine] consolidate_memory OK for {key} with {len(notes)} notes", flush=True)
    return summary_doc


def list_recent_memories(
    user_id: Optional[str] = None, limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Lista memorias crudas recientes (para debug o para que Natacha
    pueda leer contexto rápido sin escanear toda la colección).

    - Si puede, filtra por user_id.
    - Si Firestore pide índice o algo falla, hace fallback a últimas globales.
    """

    def _run_query(with_user: bool) -> List[Dict[str, Any]]:
        q = db.collection(COL_RAW)

        if with_user and user_id:
            q = q.where("user_id", "==", user_id)

        q = q.order_by(
            "created_at",
            direction=firestore.Query.DESCENDING,
        ).limit(limit)

        docs = list(q.stream())
        items: List[Dict[str, Any]] = []
        for d in docs:
            data = d.to_dict() or {}
            data["id"] = d.id
            items.append(data)
        return items

    # 1) Intentar con filtro por usuario
    if user_id:
        try:
            items = _run_query(with_user=True)
            if items:
                return items
        except Exception:
            pass

    # 2) Fallback sin filtro (global)
    try:
        return _run_query(with_user=False)
    except Exception:
        return []


def save_system_rule(note: str, version: str = "v1") -> str:
    """
    Guarda reglas internas (por ejemplo: protocolo, políticas de Natacha, etc.).
    """
    doc = db.collection(COL_SYSTEM).document(version)
    doc.set(
        {
            "rule": note,
            "version": version,
            "created_at": _utc_iso(),
        }
    )
    return "ok"
