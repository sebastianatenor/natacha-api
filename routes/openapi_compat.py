from fastapi import APIRouter, Request
from fastapi.openapi.utils import get_openapi
import os

router = APIRouter()

@router.get("/openapi.v1.json")
def openapi_v1(request: Request):
    app = request.app
    schema = get_openapi(title=getattr(app,"title","Natacha API"),
                         version=getattr(app,"version","1.0.0"),
                         routes=app.routes)
    public = os.getenv("OPENAPI_PUBLIC_URL","").rstrip("/")
    if public:
        schema["servers"] = [{"url": public}]
    schema["openapi"] = "3.1.0"
    return schema
