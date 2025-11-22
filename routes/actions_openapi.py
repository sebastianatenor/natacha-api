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

    # People (contactos / perfiles)
    "/people/save",
    "/people/get",
    "/people/search",

    # Projects (proyectos)
    "/projects/save",
    "/projects/get",
    "/projects/search",

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
            "Incluye salud, memoria, núcleo de respuesta, tasks, people, projects y ops."
        ),
        routes=app.routes,
    )

    # Filtramos paths
    paths = full_schema.get("paths", {})
    filtered_paths = {p: v for p, v in paths.items() if p in ALLOWED_PATHS}
    full_schema["paths"] = filtered_paths

    # 🔴 FIX 1: agregar servers con URL HTTPS pública (requisito de Actions)
    full_schema["servers"] = [
        {"url": "https://natacha-api-422255208682.us-central1.run.app"}
    ]

    # 🔴 FIX 2: definir esquemas formales para people.save y projects.save
    components = full_schema.setdefault("components", {}).setdefault("schemas", {})

    # Esquema para /people/save
    components["PeoplePayload"] = {
        "title": "PeoplePayload",
        "type": "object",
        "properties": {
            "id": {"type": "string", "title": "Id", "description": "ID interno único del contacto"},
            "name": {"type": "string", "title": "Name", "description": "Nombre de la persona"},
            "role": {"type": "string", "title": "Role", "description": "Rol / cargo"},
            "location": {"type": "string", "title": "Location", "description": "Ciudad / región"},
            "notes": {"type": "string", "title": "Notes", "description": "Notas relevantes"},
            "tags": {
                "type": "array",
                "title": "Tags",
                "items": {"type": "string"},
                "description": "Etiquetas tipo ['china','xcmg','llvc']",
            },
        },
        "required": ["id"],
    }

    # Esquema para /projects/save
    components["ProjectPayload"] = {
        "title": "ProjectPayload",
        "type": "object",
        "properties": {
            "id": {"type": "string", "title": "Id", "description": "ID único del proyecto (ej. 'LLVC')"},
            "name": {"type": "string", "title": "Name", "description": "Nombre del proyecto"},
            "status": {"type": "string", "title": "Status", "description": "Estado actual (activo, idea, pausado, etc.)"},
            "focus": {
                "type": "array",
                "title": "Focus",
                "items": {"type": "string"},
                "description": "Áreas de foco (ej. ['importaciones','maquinaria'])",
            },
            "notes": {"type": "string", "title": "Notes", "description": "Notas generales del proyecto"},
            "risks": {
                "type": "array",
                "title": "Risks",
                "items": {"type": "string"},
                "description": "Riesgos principales",
            },
            "next_steps": {
                "type": "array",
                "title": "NextSteps",
                "items": {"type": "string"},
                "description": "Próximos pasos a seguir",
            },
        },
        "required": ["id"],
    }

    # Forzar que los endpoints /people/save y /projects/save usen esos schemas
    try:
        full_schema["paths"]["/people/save"]["post"]["requestBody"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/PeoplePayload"
        }
    except KeyError:
        pass

    try:
        full_schema["paths"]["/projects/save"]["post"]["requestBody"]["content"]["application/json"]["schema"] = {
            "$ref": "#/components/schemas/ProjectPayload"
        }
    except KeyError:
        pass

    return full_schema


@router.get("/openapi.json", include_in_schema=False)
async def actions_openapi_json(request: Request):
    """Devuelve el esquema OpenAPI filtrado para ser usado como Actions spec."""
    return _build_actions_schema(request.app)
