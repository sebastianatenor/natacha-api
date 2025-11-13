from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from routes.actions_routes import router as actions_router

app = FastAPI(
    title="Natacha Actions API",
    version="1.0.0",
    description="Minimal Actions API for OpenAI (health, memory, tasks).",
)

app.include_router(actions_router)


def custom_openapi():
    """
    OpenAPI reducido con server fijo para Cloud Run.
    """
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="Natacha Actions API",
        version="1.0.0",
        description="Minimal Actions API for OpenAI (health, memory, tasks).",
        routes=app.routes,
    )

    schema["servers"] = [
        {"url": "https://natacha-actions-422255208682.us-central1.run.app"}
    ]

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi
