import os
# == Canonical resolver (no hardcodes) ==
import os
from pathlib import Path

def _resolve_base() -> str:
    # 1) env
    v = os.getenv("NATACHA_CONTEXT_API") or os.getenv("CANON")
    if v: return v
    # 2) REGISTRY.md
    reg = os.path.expanduser("~/REGISTRY.md")
    try:
        with open(reg, "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("- URL producción:"):
                    return line.split(":",1)[1].strip()
    except Exception:
        pass
    # 3) vacío: que el caller falle visiblemente si intenta usarlo
    return ""
BASE = _resolve_base()
# == end resolver ==
BASE = _resolve_base()
#!/usr/bin/env python3
import json
import urllib.request
URL = f"{BASE}/ops/insights?limit=50"

with urllib.request.urlopen(URL) as resp:
    data = json.load(resp)

with open("last_context.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Contexto operativo descargado en last_context.json")
