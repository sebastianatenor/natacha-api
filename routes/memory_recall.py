from fastapi import APIRouter, Query
from ops.memory.search import search_memory
from ops.memory.recall import (
    recall_recent,
    recall_decisions,
    recall_by_subsystem,
)

router = APIRouter(tags=["memory"])


# =========================================================
# EXISTENTES (NO SE TOCAN)
# =========================================================

@router.get("/memory/recall/recent")
def recall_recent_api(limit: int = 20):
    return {
        "status": "ok",
        "mode": "recent",
        "events": recall_recent(limit),
    }


@router.get("/memory/recall/decisions")
def recall_decisions_api(limit: int = 10):
    return {
        "status": "ok",
        "mode": "decisions",
        "events": recall_decisions(limit),
    }


# =========================================================
# 🔍 SEARCH (DEBE IR ANTES DEL {subsystem})
# =========================================================

@router.get("/memory/recall/search")
def recall_search_api(
    query: str = Query(..., description="Texto a buscar en memoria"),
    limit: int = 10,
):
    """
    Search seguro:
    1) Intenta semántico si existe
    2) Fallback a texto plano
    """

    # --- Intento semántico (si está disponible)
    try:
        from unified_core.semantic_search import semantic_search

        results = semantic_search(query=query, top_k=limit)
        return {
            "status": "ok",
            "mode": "semantic",
            "query": query,
            "count": len(results),
            "events": results,
        }

    except Exception:
        # --- Fallback textual
        from ops.timeline.reader import read_events

        events = read_events()
        hits = [
            e for e in events
            if query.lower() in str(e).lower()
        ]

        return {
            "status": "ok",
            "mode": "timeline_fallback",
            "query": query,
            "count": min(len(hits), limit),
            "events": hits[-limit:],
        }


# =========================================================
# SUBSYSTEM (SIEMPRE AL FINAL)
# =========================================================

@router.get("/memory/recall/{subsystem}")
def recall_subsystem_api(subsystem: str, limit: int = 10):
    return {
        "status": "ok",
        "mode": "subsystem",
        "subsystem": subsystem,
        "events": recall_by_subsystem(subsystem, limit),
    }
