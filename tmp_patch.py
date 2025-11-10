import re, pathlib

path = pathlib.Path("service_main.py")
text = path.read_text()

# Quitamos cualquier import previo de slowapi
text = re.sub(r"^from slowapi[^\n]*\n?", "", text, flags=re.M)
text = re.sub(r"^    from slowapi[^\n]*\n?", "", text, flags=re.M)

# Insertamos un bloque único y seguro después del primer bloque de imports
insert_block = """\
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

# Insertamos después de la primera tanda de imports (por ejemplo, después de la línea que contiene "from fastapi")
lines = text.splitlines()
for i, line in enumerate(lines):
    if "from fastapi" in line:
        lines.insert(i + 1, insert_block)
        break

path.write_text("\n".join(lines))
print("✅ Bloque slowapi insertado con fallback seguro")
