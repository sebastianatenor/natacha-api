from fastapi import APIRouter
import requests
import os

router = APIRouter(prefix="/calendar", tags=["calendar"])

# URL de tu servicio calendar (Cloud Run)
CALENDAR_BASE = os.getenv(
    "NATACHA_CALENDAR_URL",
    "https://natacha-calendar-service-422255208682.us-central1.run.app"
)

GOOGLE_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "asistente-sebastian")


# ---------------------------------------------------------
# 1) HEALTH LOCAL DEL MÓDULO CALENDAR
# ---------------------------------------------------------
@router.get("/health")
def calendar_health():
    return {
        "status": "ok",
        "service": "natacha-api-calendar-module",
        "calendar_service_url": CALENDAR_BASE,
    }


# ---------------------------------------------------------
# 2) PROXY → /calendar/proxy/health
# ---------------------------------------------------------
@router.get("/proxy/health")
def calendar_proxy_health():
    """
    Verifica que el servicio natacha-calendar-service esté funcionando
    y accesible desde natacha-api.
    """
    try:
        r = requests.get(f"{CALENDAR_BASE}/health", timeout=5)
        return {
            "proxy_status": "ok",
            "target_status": r.json(),
            "target_url": CALENDAR_BASE,
        }
    except Exception as e:
        return {
            "proxy_status": "error",
            "target_url": CALENDAR_BASE,
            "detail": str(e),
        }


# ---------------------------------------------------------
# 3) PROXY → LIST EVENTS
# ---------------------------------------------------------
@router.get("/proxy/list")
def calendar_proxy_list():
    """
    Llama al endpoint real de natacha-calendar-service que lista
    eventos del Google Calendar conectado.
    """
    try:
        r = requests.get(f"{CALENDAR_BASE}/calendar/list", timeout=10)
        return {
            "proxy_status": "ok",
            "events": r.json(),
            "target_url": CALENDAR_BASE,
        }
    except Exception as e:
        return {
            "proxy_status": "error",
            "target_url": CALENDAR_BASE,
            "detail": str(e),
        }


# ---------------------------------------------------------
# 4) STATUS DEL MÓDULO (STUB PERO SE MANTIENE)
# ---------------------------------------------------------
@router.get("/status")
def calendar_status():
    return {
        "status": "active",
        "project_id": GOOGLE_PROJECT_ID,
        "calendar_service_url": CALENDAR_BASE,
        "message": (
            "Calendar integration active. Proxies disponibles: "
            "/calendar/proxy/health y /calendar/proxy/list"
        ),
    }
