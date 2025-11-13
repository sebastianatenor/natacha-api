from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import os

router = APIRouter()

@router.get("/openapi.json")
def openapi_override(request: Request):
    app = request.app

    if app.openapi_schema:
        return JSONResponse(app.openapi_schema)

    # Generar el esquema normal
    schema = get_openapi(
        title=getattr(app, "title", "Natacha API"),
        version="1.0.0",
        routes=app.routes,
    )

    # AGREGAR servers !!!
    base_url = os.getenv("PUBLIC_BASE_URL", "").rstrip("/") or \
               os.getenv("RUN_BASE_URL", "").rstrip("/") or \
               request.url_for("openapi_override").replace("/openapi.json", "")

    schema["servers"] = [{"url": base_url}]

    app.openapi_schema = schema
    return JSONResponse(schema)
