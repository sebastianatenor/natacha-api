import json

PATH = "memory_store.jsonl"

def has_bad_unicode(s: str) -> bool:
    try:
        s.encode("utf-8")
        return False
    except UnicodeEncodeError:
        return True

bad_lines = []

with open(PATH, "r") as f:
    for line_num, line in enumerate(f, start=1):
        line = line.strip()
        if not line:
            continue

        try:
            obj = json.loads(line)
        except Exception:
            continue

        # Revisar todos los campos posibles
        fields = []

        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, str):
                    fields.append((k, v))
                if isinstance(v, list):
                    for x in v:
                        if isinstance(x, str):
                            fields.append((k, x))

        for field_name, text in fields:
            if has_bad_unicode(text):
                bad_lines.append((line_num, field_name, text))

print("\n=== RESULTADOS ===")
if not bad_lines:
    print("✔ No se encontraron caracteres ilegales.")
else:
    print(f"⚠ Se encontraron {len(bad_lines)} líneas con Unicode inválido:\n")
    for ln, field, txt in bad_lines:
        print(f" - Línea {ln}, campo '{field}': {repr(txt)[:200]}")
