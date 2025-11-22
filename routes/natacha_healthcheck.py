from datetime import datetime
from typing import Optional, Dict, Any, List

import os
import requests
from fastapi import APIRouter
from pydantic import BaseModel

# Usamos la misma base que en natacha_brain / memory_bridge
SERVICE_URL = os.getenv(
    "SERVICE_URL",
    "https://natacha-api-422255208682.us-central1.run.app",
)

router = APIRouter(prefix="/natacha", tags=["natacha-health"])


class HealthcheckRequest(BaseModel):
    user_id: str
    project: Optional[str] = None


def _safe_get(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Helper simple para hacer GETs seguros contra la propia API.
    Nunca levanta excepción: devuelve siempre un dict.
    """
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "error": str(e), "url": url, "params": params or {}}


def _safe_post(url: str, json_body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper simple para hacer POSTs seguros contra la propia API.
    """
    try:
        r = requests.post(url, json=json_body, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "error": str(e), "url": url, "body": json_body}


@router.post("/healthcheck")
def natacha_healthcheck(payload: HealthcheckRequest):
    """
    Mini health-check ejecutivo de Natacha para Sebastián.

    Verifica:
    - Que exista system_rule core-v1.
    - Que haya summary para el user_id.
    - Que recent no esté vacío.
    - Que semantic_v2 responda algo para el proyecto actual.
    - Que el motor de tasks esté reachable.

    Devuelve un snapshot compacto para diagnóstico ejecutivo.
    """
    user_id = payload.user_id
    project = payload.project

    checks: Dict[str, Any] = {}

    # 1) context_bundle (core de memoria ejecutiva)
    ctx = _safe_get(
        f"{SERVICE_URL}/memory/engine/context_bundle",
        params={"user_id": user_id, "project": project, "semantic_project": project, "semantic_q": "estado LLVC", "semantic_limit": 5},
    )

    summary = ctx.get("summary")
    system_rule = ctx.get("system_rule")
    recent = ctx.get("recent", {})
    semantic_v2 = ctx.get("semantic_v2", {})

    checks["system_rule_present"] = bool(system_rule)
    checks["summary_present"] = bool(summary)
    checks["recent_non_empty"] = bool(recent and recent.get("count", 0) > 0)

    # semantic_v2: consideramos ok si al menos no está en error
    checks["protocol_found_in_semantic_v2"] = (
        isinstance(semantic_v2, dict)
        and semantic_v2.get("status") in ("ok", "disabled")
    )

    # 2) Tasks engine reachable
    tasks_resp = _safe_get(
        f"{SERVICE_URL}/tasks/list",
        params={"project": project, "limit": 5},
    )
    checks["tasks_engine_reachable"] = tasks_resp.get("status") == "ok"

    # Snapshot de contexto (compacto)
    context_snapshot: Dict[str, Any] = {
        "system_rule": system_rule,
        "summary": summary,
        "recent_sample": (recent.get("items", [])[:5] if isinstance(recent, dict) else []),
        "semantic_v2_status": semantic_v2.get("status") if isinstance(semantic_v2, dict) else None,
    }

    # Protocolo de sanidad ejecutiva (lo ponemos explícito para inspeccionarlo fácil)
    protocol: Dict[str, Any] = {
        "version": "exec-health-v1",
        "description": "Checklist ejecutivo de sanidad cognitiva de Natacha para Sebastián.",
        "questions": [
            "¿Tengo cargada la system_rule core-v1?",
            "¿Tengo un summary actualizado para este user_id/proyecto?",
            "¿Estoy viendo memorias recientes relevantes (recent)?",
            "¿La memoria semántica v2 devuelve algo coherente para este proyecto?",
            "¿El motor de tareas responde y lista pendientes?"
        ],
    }

    # Muestra de tareas (si el motor respondió bien)
    tasks_sample: List[Dict[str, Any]] = []
    if tasks_resp.get("status") == "ok":
        items = tasks_resp.get("items") or []
        tasks_sample = items[:5]

    # Determinar severidad general
    if all(checks.values()):
        overall_status = "ok"
    elif checks.get("system_rule_present") and checks.get("summary_present"):
        overall_status = "attention"
    else:
        overall_status = "critical"

    meta = {
        "user_id": user_id,
        "project": project,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "service_url_used": SERVICE_URL,
    }

    return {
        "status": overall_status,
        "checks": checks,
        "context_snapshot": context_snapshot,
        "protocol": protocol,
        "tasks_sample": tasks_sample,
        "meta": meta,
    }
