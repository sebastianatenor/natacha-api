# routes/core_routes.py
import json
import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from intelligence.startup import load_operational_context

router = APIRouter(tags=["core"])

@router.get("/dashboard/data")
def dashboard_data():
    """
    Devuelve un resumen limpio del estado operativo de Natacha,
    listo para mostrar en el dashboard visual.
    """
    api_base = os.getenv("NATACHA_CONTEXT_API", "http://127.0.0.1:8003")

    try:
        context = load_operational_context(api_base=api_base, limit=20)
    except Exception as e:
        # Intentamos fallback local
        try:
            with open("last_context.json", "r") as f:
                context = json.load(f)
        except Exception:
            raise HTTPException(status_code=500, detail=f"No se pudo obtener contexto: {e}")

    projects = []
    if not context:
        return {"projects": [], "alerts": []}
    for p in context.get("projects", []):
        name = p.get("name")
        pending = p.get("pending_tasks", 0)
        urgent = p.get("urgent_task", {}) or {}
        alerts = p.get("alerts", [])
        projects.append({
            "name": name,
            "pending_tasks": pending,
            "urgent_title": urgent.get("title"),
            "urgent_due": urgent.get("due"),
            "alerts": alerts,
        })

    raw = context.get("raw", {})
    totals = {
        "projects": len(projects),
        "tasks": raw.get("tasks", 0),
        "memories": raw.get("memories", 0),
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "projects": projects,
        "totals": totals,
    }
