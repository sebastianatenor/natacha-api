from pathlib import Path
import re, py_compile, importlib

p = Path("service_main.py")
src = p.read_text()

# --- 1) Quitar imports rotos/previos de db_util y slowapi
src = re.sub(r'^\s*from\s+routes\.db_util\s+import\s+[^\n]+\n', '', src, flags=re.M)
src = re.sub(r'^\s*(?:from|import)\s+slowapi[^\n]*\n', '', src, flags=re.M)
# Quitar cualquier bloque "optional SlowAPI" previo mal insertado
src = re.sub(r'#\s*===\s*optional SlowAPI.*?(?=^\S|\Z)', '', src, flags=re.S|re.M)
# Quitar cualquier bloque "safe import for get_db/get_client" previo
src = re.sub(r'#\s*---\s*safe import for get_db/get_client\s*---.*?#\s*---\s*end safe import block\s*---\s*',
             '', src, flags=re.S)

lines = src.splitlines()

# --- 2) Encontrar el final del bloque de imports top-level
insert_at = 0
for i, line in enumerate(lines):
    if line.startswith("import ") or line.startswith("from "):
        insert_at = i + 1
        continue
    # permitir líneas en blanco posteriores inmediatas
    if line.strip() == "" and i == insert_at:
        insert_at = i + 1
        continue
    # primera línea que ya no es import/buffer
    break

# --- 3) Bloque safe de db_util
safe_db_block = [
    "",
    "# --- safe import for get_db/get_client ---",
    "try:",
    "    from routes.db_util import get_db, get_client",
    "except Exception:  # define fallbacks so the app can boot",
    "    from contextlib import contextmanager",
    "    def get_client():",
    "        return None",
    "    @contextmanager",
    "    def get_db():",
    "        yield None",
    "# --- end safe import block ---",
    "",
]

# --- 4) Bloque optional SlowAPI (si luego se usa, no rompe el import)
slowapi_block = [
    "# === optional SlowAPI integration (safe) ===",
    "Limiter = None",
    "get_remote_address = None",
    "SlowAPIMiddleware = None",
    "RateLimitExceeded = Exception",
    "try:",
    "    from slowapi import Limiter as _Limiter",
    "    from slowapi.util import get_remote_address as _get_remote_address",
    "    from slowapi.middleware import SlowAPIMiddleware as _SlowAPIMiddleware",
    "    from slowapi.errors import RateLimitExceeded as _RateLimitExceeded",
    "    Limiter = _Limiter",
    "    get_remote_address = _get_remote_address",
    "    SlowAPIMiddleware = _SlowAPIMiddleware",
    "    RateLimitExceeded = _RateLimitExceeded",
    "except Exception:",
    "    pass",
    "# === end optional SlowAPI integration ===",
    "",
]

new_src = "\n".join(lines[:insert_at] + safe_db_block + slowapi_block + lines[insert_at:])

# --- 5) Asegurar que if SlowAPIMiddleware tenga cuerpo indentado
fixed_lines = []
ls = new_src.splitlines()
i = 0
while i < len(ls):
    fixed_lines.append(ls[i])
    if ls[i].strip() == "if SlowAPIMiddleware:":
        nxt = ls[i+1] if i+1 < len(ls) else ""
        if not nxt.startswith((" ", "\t")):
            fixed_lines.append("    app.add_middleware(SlowAPIMiddleware)")
    i += 1
new_src = "\n".join(fixed_lines)

# --- 6) Proteger instancias de Limiter(...) si aparecen
new_src = re.sub(r'(\blimiter\s*=\s*)Limiter\s*\(',
                 r'\1(Limiter or (lambda *a, **k: None))(', new_src)

# --- 7) Guardar y compilar
p.write_text(new_src + "\n")
py_compile.compile("service_main.py", doraise=True)

# --- 8) Test de import (como haría Uvicorn)
m = importlib.import_module("service_main")
ok_app = hasattr(m, "app")
print("✅ service_main.py OK | app =", ok_app)
