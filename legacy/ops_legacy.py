import os
# == Canonical resolver (no hardcodes) ==
import os
from pathlib import Path

def _resolve_base() -> str:
    # 1) env
    v = os.getenv("NATACHA_CONTEXT_API") or os.getenv("CANON")
    if v: return v
    # 2) REGISTRY.md
    reg = os.path.expanduser("~/REGISTRY.md")
    try:
        with open(reg, "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("- URL producción:"):
                    return line.split(":",1)[1].strip()
    except Exception:
        pass
    # 3) vacío: que el caller falle visiblemente si intenta usarlo
    return ""
BASE = _resolve_base()
# == end resolver ==
BASE = _resolve_base()
from fastapi import APIRouter

from natacha_base import observer  # si existe el módulo para aprendizaje
from natacha_base import gcp_utils

router = APIRouter()


@router.post("/ops/sync_environment")
def sync_environment():
    """
    Sincroniza la infraestructura de Natacha en GCP:
    - Secret Manager
    - Cloud Scheduler
    - Pub/Sub
    - Service Accounts en Cloud Run
    - Aprendizaje forzado si hubo cambios
    """
    results = []

    # 1️⃣ Verificar o crear secretos
    required_secrets = ["SERVICE_ACCOUNT_KEY", "META_WHATSAPP_TOKEN", "NOTION_TOKEN"]
    for secret in required_secrets:
        ok = gcp_utils.ensure_secret(secret)
        results.append(
            {"type": "secret", "name": secret, "status": "ok" if ok else "created"}
        )

    # 2️⃣ Verificar o crear job en Cloud Scheduler
    job_ok = gcp_utils.ensure_scheduler_job(
        name="natacha-daily-learn",
        schedule="0 3 * * *",
        uri = f"{BASE}/ops/force_learn",
        service_account="natacha-automation@asistente-sebastian.iam.gserviceaccount.com",
    )
    results.append(
        {
            "type": "scheduler",
            "name": "natacha-daily-learn",
            "status": "ok" if job_ok else "created",
        }
    )

    # 3️⃣ Verificar o crear Pub/Sub topic
    topic_ok = gcp_utils.ensure_pubsub_topic("natacha-daily-report")
    results.append(
        {
            "type": "pubsub",
            "name": "natacha-daily-report",
            "status": "ok" if topic_ok else "created",
        }
    )

    # 4️⃣ Verificar service account de Cloud Run
    sa_ok = gcp_utils.ensure_run_service_account(
        "natacha-api", "natacha-automation@asistente-sebastian.iam.gserviceaccount.com"
    )
    results.append({"type": "service-account", "status": "ok" if sa_ok else "updated"})

    # 5️⃣ Si algo cambió, forzar aprendizaje
    updated = any(r["status"] != "ok" for r in results)
    learn_result = None
    if updated:
        try:
            learn_result = observer.run_learning_cycle()
        except Exception as e:
            learn_result = {"error": str(e)}

    return {
        "status": "completed",
        "updates": results,
        "learning_triggered": bool(learn_result),
        "timestamp": gcp_utils.now(),
    }
