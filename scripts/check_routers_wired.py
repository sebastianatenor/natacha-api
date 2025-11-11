"""
Falla si hay APIRouter definidos en routes/*.py que no están incluidos en service_main.app
Reglas simples: busca `router = APIRouter` y luego exige un `include_router` correspondiente.
"""
import re, pathlib, sys

routes = pathlib.Path("routes")
sm = pathlib.Path("service_main.py").read_text(encoding="utf-8")

errors = []
for f in routes.glob("*.py"):
    txt = f.read_text(encoding="utf-8")
    if re.search(r"\bAPIRouter\s*\(", txt) and "router =" in txt:
        # asunción: `from routes.X import router as <alias>` o include por módulo
        mod = f.stem
        # Consideramos incluido si aparece include_router y el nombre del módulo en la línea de import
        imported = re.search(rf"from\s+routes\.{re.escape(mod)}\s+import\s+router\s+as\s+\w+", sm)
        included = re.search(rf"include_router\([^)]*{mod}.*router|\binclude_router\([^)]*ops_self_router\)", sm)
        # flexible: si hace import router directo sin alias y luego include_router(router)
        imported_direct = re.search(rf"from\s+routes\.{re.escape(mod)}\s+import\s+router\b", sm)
        included_direct = re.search(r"\binclude_router\(\s*router\s*\)", sm)

        if not ((imported and included) or (imported_direct and included_direct)):
            # último intento: hay cualquier include_router que mencione el módulo?
            if not re.search(rf"include_router\([^)]*{re.escape(mod)}", sm):
                errors.append(mod)

if errors:
    print("Routers no incluidos en service_main:", ", ".join(sorted(errors)))
    sys.exit(1)
print("OK: todos los routers están incluidos.")
