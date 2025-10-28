from fastapi import APIRouter
from natacha_base import gcp_utils
from natacha_base import observer  # si existe el módulo para aprendizaje

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
        results.append({
            "type": "secret",
            "name": secret,
            "status": "ok" if ok else "created"
        })

    # 2️⃣ Verificar o crear job en Cloud Scheduler
    job_ok = gcp_utils.ensure_scheduler_job(
        name="natacha-daily-learn",
        schedule="0 3 * * *",
        uri="https://natacha-api-422255208682.us-central1.run.app/ops/force_learn",
        service_account="natacha-automation@asistente-sebastian.iam.gserviceaccount.com"
    )
    results.append({
        "type": "scheduler",
        "name": "natacha-daily-learn",
        "status": "ok" if job_ok else "created"
    })

    # 3️⃣ Verificar o crear Pub/Sub topic
    topic_ok = gcp_utils.ensure_pubsub_topic("natacha-daily-report")
    results.append({
        "type": "pubsub",
        "name": "natacha-daily-report",
        "status": "ok" if topic_ok else "created"
    })

    # 4️⃣ Verificar service account de Cloud Run
    sa_ok = gcp_utils.ensure_run_service_account(
        "natacha-api", 
        "natacha-automation@asistente-sebastian.iam.gserviceaccount.com"
    )
    results.append({
        "type": "service-account",
        "status": "ok" if sa_ok else "updated"
    })

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
        "timestamp": gcp_utils.now()
    }
