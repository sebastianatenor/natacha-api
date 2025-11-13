from typing import Dict

from fastapi import APIRouter, Request
from fastapi.openapi.utils import get_openapi

router = APIRouter(prefix="/actions", tags=["actions-openapi"])

ALLOWED_PATHS = [
    "/health",
    "/natacha/respond",
    "/memory/engine/context_bundle",
    "/memory/engine/raw",
    "/memory/engine/recent",
    "/memory/engine/consolidate",
    "/memory/engine/system",
]


def _build_actions_schema(app) -> Dict:
    full_schema = get_openapi(
        title="Natacha Actions API",
        version="1.0.0",
        description="Esquema reducido para ChatGPT Actions",
        routes=app.routes,
    )

    paths = full_schema.get("paths", {})
    filtered_paths = {p: v for p, v in paths.items() if p in ALLOWED_PATHS}
    full_schema["paths"] = filtered_paths

    return full_schema


@router.get("/openapi.json", include_in_schema=False)
async def actions_openapi_json(request: Request):
    return _build_actions_schema(request.app)
