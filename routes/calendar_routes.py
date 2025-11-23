from fastapi import APIRouter
import os

router = APIRouter(prefix="/calendar", tags=["calendar"])

GOOGLE_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "asistente-sebastian")


@router.get("/status")
def calendar_status():
    """
    Endpoint de estado de la integración con Google Calendar.

    Por ahora es solo un stub que refleja lo que documentamos en REGISTRY:
    - La integración oficial va a vivir dentro de natacha-api.
    - El servicio separado 'natacha-calendar-service' se considera legado/experimental.
    - La imagen gcr.io/asistente-sebastian/natacha-calendar hoy no existe.

    Más adelante, este endpoint se reemplaza/expande con chequeos reales contra
    la API de Google Calendar (credenciales, scopes, agendas, etc.).
    """
    return {
        "status": "planned",
        "project_id": GOOGLE_PROJECT_ID,
        "message": (
            "Integración con Google Calendar planificada dentro de natacha-api. "
            "El servicio externo 'natacha-calendar-service' se considera legado y la "
            "imagen gcr.io/asistente-sebastian/natacha-calendar hoy no existe. "
            "Este endpoint es un stub inicial para empezar a cablear Calendar."
        ),
    }
