from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from google.cloud import firestore
from routes.memory_routes import get_db  # reutilizamos credenciales/cliente

router = APIRouter(tags=["v1"])

@router.get("/memory/search")
def memory_search_v1(
    project: Optional[str] = Query(default=None),
    channel: Optional[str] = Query(default=None),
    query: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100)
) -> Dict[str, Any]:
    """
    v1: Trae hasta 200 docs por timestamp y filtra en Python para evitar índices compuestos.
    """
    try:
        db = get_db()
        col = db.collection("assistant_memory")
        # Traemos por timestamp DESC (single-field index) y luego filtramos en memoria
        q = col.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(200)
        docs = list(q.stream())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"firestore error: {e!r}")

    items: List[Dict[str, Any]] = []
    q_lower = (query or "").lower()

    for d in docs:
        data = d.to_dict() or {}
        data["id"] = d.id

        if project and (data.get("project") != project):
            continue
        if channel and (data.get("channel") != channel):
            continue
        if q_lower:
            haystack = f"{data.get('summary','')} {data.get('detail','')}".lower()
            if q_lower not in haystack:
                continue

        items.append(data)
        if len(items) >= limit:
            break

    return {"status": "ok", "count": len(items), "items": items}
