from typing import Optional
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import requests
from fastapi import APIRouter, Body, HTTPException, Query

# usamos el cliente centralizado, como en tasks_routes
from app.utils.firestore_client import get_client

router = APIRouter(tags=["auto"])

# base del contenedor en Cloud Run
BASE_DIR = Path("/app") if Path("/app").exists() else Path(".")
SAFE_DIRS = [BASE_DIR, BASE_DIR / "routes", BASE_DIR / "scripts"]

# URL pública (fallback)
PUBLIC_BASE = os.getenv(
    "NATACHA_PUBLIC_BASE",
    "https://natacha-api-422255208682.us-central1.run.app",
)
# URL interna (dentro del mismo servicio)
LOCAL_BASE = os.getenv("NATACHA_LOCAL_BASE", "http://127.0.0.1:8080")

@router.get("/auto/list_repo")
def auto_list_repo(subdir: str = Query(".", description="Subcarpeta dentro del repo")):
    root = (BASE_DIR / subdir).resolve()
    if not root.exists():
        raise HTTPException(status_code=404, detail=f"{subdir} no existe")
    items = []
    for p in sorted(root.iterdir()):
        items.append(
            {
                "name": p.name,
                "is_dir": p.is_dir(),
                "size": p.stat().st_size if p.is_file() else 0,
            }
        )
    return {"status": "ok", "base": str(root), "items": items}

@router.get("/auto/show_file")
def auto_show_file(path: str = Query(..., description="Ruta relativa dentro del repo")):
    file_path = (BASE_DIR / path).resolve()
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"{path} no encontrado")
    content = file_path.read_text(encoding="utf-8")
    return {"status": "ok", "path": path, "content": content, "size": len(content)}

def _detect_backups() -> List[dict]:
    """
    Escanea el repo y detecta archivos tipo backup, duplicados o con timestamp.
    NO borra, solo detecta.
    """
    suspects: List[dict] = []
    for folder in SAFE_DIRS:
        if not folder.exists():
            continue
        for p in folder.rglob("*"):
            if not p.is_file():
                continue
            name = p.name
            if (
                ".bak" in name
                or name.endswith("~")
                or name.endswith(".old")
                or ".backup" in name
                or ".bak." in name
            ):
                suspects.append(
                    {
                        "path": str(p),
                        "size": p.stat().st_size,
                        "mtime": datetime.fromtimestamp(
                            p.stat().st_mtime, tz=timezone.utc
                        ).isoformat(),
                    }
                )
    return suspects

def _log_auto(event: str, meta: dict):
    """Registra en assistant_ops para que quede historia."""
    db = get_client()
    db.collection("assistant_ops").add(
        {
            "kind": "auto",
            "event": event,
            "meta": meta,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )

def _post_json(url: str, payload: dict, timeout: float = 4.0) -> Optional[requests.Response]:
    try:
        return requests.post(url, json=payload, timeout=timeout)
    except Exception:
        return None

def _create_internal_task(title: str, detail: str, backups_count: int) -> dict:
    """
    Crea una tarea usando el endpoint interno /tasks/add.
    PRIORIDAD:
      1) http://127.0.0.1:8080/tasks/add
      2) https://natacha-api.../tasks/add
      3) fallback -> /memory/add
    El payload respeta lo que hoy acepta tasks_routes.py.
    """
    task_payload = {
        "title": title,
        "detail": detail,
        "project": "Natacha",
        "channel": "auto",
        "state": "pending",
        "due": "",
        "source": "internal",
        "user_id": "system",
    }

    # 1) LOCAL
    r = _post_json(f"{LOCAL_BASE}/tasks/add", task_payload, timeout=3.5)
    if r is not None and r.status_code == 200:
        return {"source": "local", "status": r.status_code}

    # 2) PÚBLICO
    r = _post_json(f"{PUBLIC_BASE}/tasks/add", task_payload, timeout=4.5)
    if r is not None and r.status_code == 200:
        return {"source": "public", "status": r.status_code}

    # 3) FALLBACK -> MEMORIA
    mem_payload = {
        "summary": "AUTO: no se pudo crear tarea de limpieza de backups",
        "detail": f"Había {backups_count} archivos sospechosos.",
        "project": "Natacha",
        "channel": "auto",
    }
    _post_json(f"{PUBLIC_BASE}/memory/add", mem_payload, timeout=3.0)
    return {"source": "fallback", "status": 500}

@router.post("/auto/plan_refactor")
def auto_plan_refactor(payload: dict = Body(...)):
    """
    Analiza el repo y propone una limpieza/refactor.
    - detecta backups
    - genera un reporte
    - crea una tarea en /tasks/add (local → pública → memory)
    """
    goal = (payload.get("goal") or "refactor") if payload else "refactor"

    backups = _detect_backups()
    backups_count = len(backups)

    # armamos un detail compacto para la tarea
    detail_lines = [
        f"Se encontraron {backups_count} archivos sospechosos (bak, old, ~).",
        f"Goal solicitado: {goal}",
    ]
    if backups:
        detail_lines.append("Ejemplos:")
        for item in backups[:5]:
            detail_lines.append(f"- {item['path']} ({item['size']} bytes)")
    detail_text = "\n".join(detail_lines)

    # crear la tarea interna
    task_result = _create_internal_task(
        title="Auto-refactor: limpiar backups",
        detail=detail_text,
        backups_count=backups_count,
    )

    # loguear en assistant_ops
    _log_auto(
        "plan_refactor",
        {"goal": goal, "backups_found": backups_count, "task_result": task_result},
    )

    # guardar el plan y devolver id
    plan_id = _store_refactor_plan(goal, backups)
    sample = backups[:5] if backups else []

    return {
        "status": "ok",
        "message": "análisis auto-refactor generado",
        "backups_found": backups_count,
        "task_created": task_result,
        "plan_id": plan_id,
        "sample": sample,
    }

def auto_log_action(payload: dict = Body(...)):
    """
    Endpoint genérico para registrar acciones automáticas o de mantenimiento.
    """
    meta = payload or {}
    _log_auto("manual-log", meta)
    return {
        "status": "ok",
        "logged": meta,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

def _store_refactor_plan(goal: str, backups: list) -> str:
    """
    Guarda el plan de refactor en Firestore para revisión humana.
    NO ejecuta nada; solo persiste el plan y devuelve el id del doc.
    """
    db = get_client()
    doc = {
        "kind": "auto-refactor-plan",
        "goal": goal,
        "backups": backups,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        # add() puede devolver un tuple (write_result, ref) o variar por SDK
        res = db.collection("assistant_ops").add(doc)  # usa tu colección favorita si preferís una dedicada
        # Intentar obtener un id robustamente
        if isinstance(res, tuple):
            # (update_time, DocumentReference)
            ref = res[1]
            return getattr(ref, "id", str(ref))
        return getattr(res, "id", str(res))
    except Exception:
        # En caso de fallo, igual devolvemos algo trazable
        return "error-writing-refactor-plan"
