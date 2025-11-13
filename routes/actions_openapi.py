from typing import Dict

from fastapi import APIRouter, Request
from fastapi.openapi.utils import get_openapi

router = APIRouter(prefix="/actions", tags=["actions-openapi"])

# Rutas que exponemos a ChatGPT Actions (máx ~30 operaciones)
ALLOWED_PATHS = [
    # Salud básica
    "/health",
    "/meta",

    # Núcleo de Natacha
    "/natacha/respond",

    # Motor de memoria
    "/memory/engine/context_bundle",
    "/memory/engine/raw",
    "/memory/engine/recent",
    "/memory/engine/consolidate",
    "/memory/engine/system",

    # Tasks (gestión de tareas)
    "/tasks/add",
    "/tasks/list",
    "/tasks/update",

    # Ops (diagnóstico de la propia API)
    "/ops/summary",
    "/ops/insights",
    "/ops/snapshot",
    "/ops/snapshots",
    "/ops/debug_source",
    "/ops/self_register",
]


def _build_actions_schema(app) -> Dict:
    """Construye un OpenAPI reducido solo con paths permitidos para Actions."""
    full_schema = get_openapi(
        title="Natacha Actions API",
        version="1.0.0",
        description=(
            "Esquema reducido para ChatGPT Actions de Natacha. "
            "Incluye salud, memoria, núcleo de respuesta, tasks y ops."
        ),
        routes=app.routes,
    )

    paths = full_schema.get("paths", {})
    filtered_paths = {p: v for p, v in paths.items() if p in ALLOWED_PATHS}
    full_schema["paths"] = filtered_paths

    return full_schema


@router.get("/openapi.json", include_in_schema=False)
async def actions_openapi_json(request: Request):
    """Devuelve el esquema OpenAPI filtrado para ser usado como Actions spec."""
    return _build_actions_schema(request.app)
