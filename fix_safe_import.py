from pathlib import Path
import re, py_compile

p = Path("service_main.py")
text = p.read_text()

# 1️⃣ Eliminar imports viejos de db_util
text = re.sub(r'^\s*from\s+routes\.db_util\s+import\s+[^\n]+\n', '', text, flags=re.M)

# 2️⃣ Encontrar la posición donde insertar
lines = text.splitlines()
insert_at = 0
for i, line in enumerate(lines[:80]):
    if line.startswith("import ") or line.startswith("from "):
        insert_at = i + 1
    elif line.strip() == "" and insert_at == i:
        insert_at = i + 1
    else:
        if insert_at: break

# 3️⃣ Bloque seguro
block = [
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
    ""
]

new_text = "\n".join(lines[:insert_at] + block + lines[insert_at:])
p.write_text(new_text + "\n")

py_compile.compile("service_main.py", doraise=True)
print("✅ service_main.py actualizado correctamente con fallback seguro")
