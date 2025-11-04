import sys, json
from pathlib import Path

# 👇 asegurar que el proyecto raíz esté en sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from fastapi.openapi.utils import get_openapi
from natacha_app import app

# 1) generar el esquema base
schema = get_openapi(
    title="Natacha API",
    version="1.0.0",
    description="API operativa de Natacha (memoria, tareas, ops, dashboard).",
    routes=app.routes,
)

# 2) forzar servers
schema["servers"] = [
    {
        "url": "https://natacha-api-422255208682.us-central1.run.app",
        "description": "Natacha API en Cloud Run",
    }
]

# 3) completar schemas faltantes
for path, methods in schema.get("paths", {}).items():
    for method, op in methods.items():
        if "requestBody" in op:
            rb = op["requestBody"]
            content = rb.get("content", {})
            if "application/json" in content:
                sch = content["application/json"].get("schema")
                if not sch or sch == {}:
                    content["application/json"]["schema"] = {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": True,
                    }
                else:
                    sch.setdefault("type", "object")
                    sch.setdefault("properties", {})

        if "responses" in op:
            for status_code, resp in op["responses"].items():
                content = resp.get("content", {})
                if "application/json" in content:
                    sch = content["application/json"].get("schema")
                    if not sch or sch == {}:
                        content["application/json"]["schema"] = {
                            "type": "object",
                            "properties": {},
                            "additionalProperties": True,
                        }
                    else:
                        sch.setdefault("type", "object")
                        sch.setdefault("properties", {})

# 4) guardar archivo estable
out = Path("openapi_stable.json")
out.write_text(json.dumps(schema, indent=2), encoding="utf-8")
print("✅ OpenAPI estable generado en", out)
