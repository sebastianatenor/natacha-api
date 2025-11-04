from fastapi import APIRouter, Response

router = APIRouter()

OPENAPI_SPEC = """openapi: 3.0.1
info:
  title: Natacha Cloud API
  version: "1.0.0"
  description: API principal de Natacha en Cloud Run (endpoints de ops)
servers:
  - url: https://natacha-api-422255208682.us-central1.run.app/
paths:
  /ops/ping:
    get:
      operationId: opsPing
      summary: Chequeo de salud básico
      responses:
        "200":
          description: OK
  /ops/smart_health:
    get:
      operationId: opsSmartHealth
      summary: Diagnóstico de sistema con memoria y tareas
      responses:
        "200":
          description: OK
  /ops/version:
    get:
      operationId: opsVersion
      summary: Versión y revisión activa del servicio
      responses:
        "200":
          description: OK
"""

@router.get("/openapi.yaml", include_in_schema=False)
async def openapi_yaml():
    return Response(content=OPENAPI_SPEC, media_type="text/yaml")
