#!/usr/bin/env python3
import json
import urllib.request

URL = "https://natacha-api-422255208682.us-central1.run.app/ops/insights?limit=50"

with urllib.request.urlopen(URL) as resp:
    data = json.load(resp)

with open("last_context.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Contexto operativo descargado en last_context.json")
