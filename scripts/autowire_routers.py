import pathlib, re, sys

ROUTES_DIR = pathlib.Path("routes")
SM_PATH    = pathlib.Path("service_main.py")

if not SM_PATH.exists():
    print("❌ service_main.py no existe. Abort.")
    sys.exit(1)

sm_txt = SM_PATH.read_text(encoding="utf-8")

# Normalizamos fin de archivo con un salto de línea
if not sm_txt.endswith("\n"):
    sm_txt += "\n"

# Detectamos módulos con `router = APIRouter(...)`
candidates = []
for f in sorted(ROUTES_DIR.glob("*.py")):
    name = f.name
    if name.startswith("_"):
        continue
    if ".bak" in name or name.endswith(".bak") or name.endswith(".bak.py"):
        continue
    mod = f.stem
    txt = f.read_text(encoding="utf-8")
    if re.search(r"\brouter\s*=\s*APIRouter\s*\(", txt):
        candidates.append(mod)

# Generamos import/include para cada módulo
added_imports  = []
added_includes = []
for mod in candidates:
    alias = f"{mod}_router"
    import_line  = f"from routes.{mod} import router as {alias}"
    include_line = f"app.include_router({alias})"

    # ya está importado?
    already_imported = re.search(rf"from\s+routes\.{re.escape(mod)}\s+import\s+router\s+as\s+\w+", sm_txt) or \
                       re.search(rf"from\s+routes\.{re.escape(mod)}\s+import\s+router\b", sm_txt)

    # ya está incluído?
    already_included = re.search(rf"include_router\([^)]*{re.escape(alias)}\)", sm_txt) or \
                       re.search(rf"include_router\([^)]*{re.escape(mod)}.*router\)", sm_txt) or \
                       re.search(r"\binclude_router\(\s*router\s*\)", sm_txt)

    # Si falta import, lo agregamos al final (es válido en Python)
    if not already_imported:
        sm_txt += f"\n{import_line}\n"
        added_imports.append(import_line)

    # Si falta include, lo agregamos al final
    if not already_included:
        sm_txt += f"{include_line}\n"
        added_includes.append(include_line)

# Guardamos solo si hubo cambios
if added_imports or added_includes:
    SM_PATH.write_text(sm_txt, encoding="utf-8")
    print("✅ Autowire aplicado.")
    if added_imports:
        print(" + Imports añadidos:")
        for l in added_imports: print("   -", l)
    if added_includes:
        print(" + Includes añadidos:")
        for l in added_includes: print("   -", l)
else:
    print("👌 Nada que hacer: todos los routers ya estaban cableados.")
