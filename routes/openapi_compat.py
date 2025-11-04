import os
from fastapi import APIRouter, Request
router = APIRouter()

@router.get("/openapi.v1.json", include_in_schema=False)
async def openapi_v1(request: Request):
    app = request.app
    schema = app.openapi()              # toma el schema actual (3.1.0)
    schema = dict(schema)               # asegurar que sea mutable
    schema["openapi"] = "3.1.0"         # forzar compat 3.0.x
    base = os.getenv("OPENAPI_PUBLIC_URL") or os.getenv("NATACHA_BASE_URL")
    if not base:
        # fallback: deducir host desde esta misma request
        u = str(request.url)
        base = u[: u.find("/openapi.v1.json")]
    schema["servers"] = [{"url": base.rstrip("/")}]
    return schema
