from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

def mount_openapi_dynamic(app, public_url: str):
    r = APIRouter()

    @r.get("/openapi.json", include_in_schema=False)
    async def openapi_json():
        schema = get_openapi(
            title="Natacha Cloud API",
            version="1.0.0",
            description="API principal de Natacha en Cloud Run",
            routes=app.routes,
        )
        schema["servers"] = [{"url": public_url.rstrip("/")}]
        return JSONResponse(
            content=schema,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "no-store",
            },
        )

    app.include_router(r)
