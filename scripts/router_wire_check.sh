#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-}"
if [[ -z "$BASE" ]]; then
  echo "❌ BASE vacío (setear NATACHA_BASE_URL en Actions vars o secrets)"; exit 1
fi

say(){ echo -e "$@"; }

say "🔎 Wirecheck contra BASE=$BASE"

# A) Salud básica
curl -sf --max-time 10 "$BASE/health" >/dev/null && say "🟢 /health OK"

# B) Probar endpoints reales, con tolerancia
ok=0; fail=0

probe(){
  local method="$1" path="$2" data="${3:-}"
  if [[ "$method" == "GET" ]]; then
    if curl -sf --max-time 15 "$BASE$path" >/dev/null; then say "🟢 $method $path"; ((ok++)); else say "🔴 $method $path"; ((fail++)); fi
  else
    if curl -sf --max-time 15 -X "$method" "$BASE$path" -H "Content-Type: application/json" -d "$data" >/dev/null; then say "🟢 $method $path"; ((ok++)); else say "🔴 $method $path"; ((fail++)); fi
  fi
}

# contract mínimo actual:
# - memory add (POST)
# - memory search (GET)  (tenés /memory/search)
# - v1 tasks search (GET)
probe POST "/memory/add" '{"summary":"ci-wirecheck","detail":"","project":"Natacha","channel":"ci"}'
probe GET  "/memory/search?limit=1"
probe GET  "/v1/tasks/search?limit=1"

say "✅ wirecheck: ok=$ok fail=$fail"
# Permitimos 1 fallo como warning sin romper el PR (por si cambia un path menor)
if (( fail > 1 )); then exit 1; fi
