import re, pathlib

p = pathlib.Path("service_main.py")
t = p.read_text()

# 1) borrar cualquier import previo de slowapi (top-level o indentado)
t = re.sub(r'^[ \t]*from slowapi[^\n]*\n?', '', t, flags=re.M)
t = re.sub(r'^[ \t]*import slowapi[^\n]*\n?', '', t, flags=re.M)

# 2) armar bloque único y seguro
block = (
    "try:\n"
    "    from slowapi import Limiter\n"
    "    from slowapi.util import get_remote_address\n"
    "    from slowapi.middleware import SlowAPIMiddleware\n"
    "    from slowapi.errors import RateLimitExceeded\n"
    "except ImportError:\n"
    "    Limiter = None\n"
    "    get_remote_address = None\n"
    "    SlowAPIMiddleware = None\n"
    "    RateLimitExceeded = Exception\n"
)

# 3) insertar el bloque después del primer import de fastapi (lo deja bien arriba)
lines = t.splitlines()
insert_at = None
for i, line in enumerate(lines[:200]):  # mirar arriba del archivo
    if line.strip().startswith("from fastapi"):
        insert_at = i + 1
        break

if insert_at is None:
    # si no encontramos ese import, lo ponemos en la línea 0
    insert_at = 0

lines.insert(insert_at, block)
new = "\n".join(lines)

# 4) asegurar que si hay uso del middleware, esté protegido (por si quedó en el archivo)
new = re.sub(
    r'^\s*app\.add_middleware\(\s*SlowAPIMiddleware\s*\)\s*$',
    "if SlowAPIMiddleware:\n    app.add_middleware(SlowAPIMiddleware)",
    new,
    flags=re.M
)

p.write_text(new)
print("✅ slowapi block fixed & guarded")
