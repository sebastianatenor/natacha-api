from fastapi import APIRouter
import os
import requests
import datetime
from typing import List, Dict, Any

router = APIRouter(prefix="/calendar", tags=["calendar"])

GOOGLE_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "asistente-sebastian")

# Servicio legado (demo) – Cloud Run
CALENDAR_SERVICE_URL = os.getenv(
    "NATACHA_CALENDAR_URL",
    "https://natacha-calendar-service-422255208682.us-central1.run.app",
)

# Modo de funcionamiento:
# - "demo": usa el servicio legado /calendar/demo-events
# - "google": intenta leer Google Calendar real (si hay credenciales y permisos)
CALENDAR_MODE = os.getenv("NATACHA_CALENDAR_MODE", "demo").lower()

# ID de calendario de Google a usar en modo "google"
# - "primary" por defecto (tu calendario principal)
GOOGLE_CALENDAR_ID = os.getenv("NATACHA_GOOGLE_CALENDAR_ID", "primary")


def _fetch_events_from_demo(hours_ahead: int = 8) -> List[Dict[str, Any]]:
    """
    Lee eventos desde el servicio legado de calendario (demo).
    GET {CALENDAR_SERVICE_URL}/calendar/demo-events?hours_ahead=...
    """
    target_url = f"{CALENDAR_SERVICE_URL}/calendar/demo-events"

    resp = requests.get(
        target_url,
        params={"hours_ahead": hours_ahead},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    # El servicio demo ya devuelve una lista de eventos normalizados
    if isinstance(data, list):
        return data

    # Si por alguna razón devuelve otra cosa, intentamos extraer 'events'
    if isinstance(data, dict) and isinstance(data.get("events"), list):
        return data["events"]

    return []


def _fetch_events_from_google(hours_ahead: int = 8) -> List[Dict[str, Any]]:
    """
    Intenta leer eventos reales desde Google Calendar.

    Requisitos (modo "google"):
    - La cuenta de servicio de Cloud Run debe tener acceso al calendario
      (compartido con la service account).
    - Debe estar habilitada la API de Calendar en el proyecto.
    - Deben existir las librerías de cliente (google-auth, google-api-python-client).
    """
    try:
        # Import dinámico para no romper si las libs no están instaladas.
        from googleapiclient.discovery import build  # type: ignore
        from google.auth import default  # type: ignore
    except Exception:
        # Si no hay librerías, devolvemos vacío y dejamos que el caller maneje el caso.
        return []

    # Credenciales por defecto del entorno (service account de Cloud Run)
    creds, _ = default(
        scopes=["https://www.googleapis.com/auth/calendar.readonly"]
    )

    service = build(
        "calendar",
        "v3",
        credentials=creds,
        cache_discovery=False,
    )

    now = datetime.datetime.utcnow()
    time_min = now.isoformat() + "Z"
    time_max = (now + datetime.timedelta(hours=hours_ahead)).isoformat() + "Z"

    events_result = (
        service.events()
        .list(
            calendarId=GOOGLE_CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
            maxResults=20,
        )
        .execute()
    )

    items = events_result.get("items", []) or []
    normalized: List[Dict[str, Any]] = []

    for ev in items:
        start = ev.get("start", {}).get("dateTime") or ev.get("start", {}).get(
            "date"
        )
        end = ev.get("end", {}).get("dateTime") or ev.get("end", {}).get("date")

        normalized.append(
            {
                "id": ev.get("id"),
                "summary": ev.get("summary"),
                "start": start,
                "end": end,
                "location": ev.get("location", ""),
                "description": ev.get("description", ""),
            }
        )

    return normalized


@router.get("/status")
def calendar_status():
    """
    Estado de la integración de calendario vista desde natacha-api.

    - Muestra el proyecto actual.
    - Indica la URL del servicio externo de calendario legado (demo).
    - Indica el modo actual (demo/google) y el calendar_id configurado.
    - Documenta los proxies disponibles.
    """
    return {
        "status": "active",
        "project_id": GOOGLE_PROJECT_ID,
        "calendar_service_url": CALENDAR_SERVICE_URL,
        "mode": CALENDAR_MODE,
        "google_calendar_id": GOOGLE_CALENDAR_ID,
        "message": (
            "Calendar integration active. "
            "Proxies disponibles: /calendar/proxy/health y /calendar/proxy/list"
        ),
    }


@router.get("/proxy/health")
def calendar_proxy_health():
    """
    Health de calendario vista desde natacha-api.

    - En modo 'demo': chequea el servicio legado de calendario.
    - En modo 'google': intenta listar 1 evento para validar acceso.
    """
    if CALENDAR_MODE == "google":
        try:
            events = _fetch_events_from_google(hours_ahead=4)
            return {
                "proxy_status": "ok",
                "mode": CALENDAR_MODE,
                "events_sample": len(events),
                "target": "google-calendar",
            }
        except Exception as e:
            return {
                "proxy_status": "error",
                "mode": CALENDAR_MODE,
                "target": "google-calendar",
                "error": str(e),
            }

    # Modo demo (actual)
    target_url = f"{CALENDAR_SERVICE_URL}/health"
    try:
        resp = requests.get(target_url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return {
            "proxy_status": "ok",
            "mode": CALENDAR_MODE,
            "target_status": data,
            "target_url": target_url,
        }
    except Exception as e:
        return {
            "proxy_status": "error",
            "mode": CALENDAR_MODE,
            "error": str(e),
            "target_url": target_url,
        }


@router.get("/proxy/list")
def calendar_proxy_list(hours_ahead: int = 8):
    """
    Lista eventos de calendario desde natacha-api.

    - En modo 'demo': usa el servicio legado /calendar/demo-events.
    - En modo 'google': lee eventos reales de Google Calendar.

    La forma de salida se mantiene compatible con lo que consume:
    - /natacha/agenda_hoy
    - /natacha/healthcheck
    """
    try:
        if CALENDAR_MODE == "google":
            events = _fetch_events_from_google(hours_ahead=hours_ahead)
            return {
                "proxy_status": "ok",
                "mode": CALENDAR_MODE,
                "events": events,
                "target": "google-calendar",
            }

        # Modo demo (por defecto)
        events = _fetch_events_from_demo(hours_ahead=hours_ahead)
        return {
            "proxy_status": "ok",
            "mode": CALENDAR_MODE,
            "events": events,
            "target_url": f"{CALENDAR_SERVICE_URL}/calendar/demo-events",
        }
    except Exception as e:
        return {
            "proxy_status": "error",
            "mode": CALENDAR_MODE,
            "events": [],
            "error": str(e),
        }
