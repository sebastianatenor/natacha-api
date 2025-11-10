import pathlib, re

p = pathlib.Path("service_main.py")
text = p.read_text()

# eliminar todos los imports existentes de slowapi
text = re.sub(r'^[ \t]*from slowapi[^\n]*\n?', '', text, flags=re.M)
text = re.sub(r'^[ \t]*import slowapi[^\n]*\n?', '', text, flags=re.M)

# bloque correcto con saltos y sangrías
block = """
# === optional SlowAPI integration (safe import) ===
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    from slowapi.middleware import SlowAPIMiddleware
    from slowapi.errors import RateLimitExceeded
except ImportError:
    Limiter = None
    get_remote_address = None
    SlowAPIMiddleware = None
    RateLimitExceeded = Exception

"""

# insertarlo después del primer bloque fastapi
lines = text.splitlines()
insert_at = 0
for i, line in enumerate(lines[:200]):
    if "from fastapi" in line:
        insert_at = i + 1
        break
lines.insert(insert_at, block)

# proteger uso de SlowAPIMiddleware
new = re.sub(
    r'^\s*app\.add_middleware\(\s*SlowAPIMiddleware\s*\)\s*$',
    "if SlowAPIMiddleware:\n    app.add_middleware(SlowAPIMiddleware)",
    "\n".join(lines),
    flags=re.M,
)

p.write_text(new)
print("✅ Bloque slowapi limpio, seguro y con saltos correctos")
