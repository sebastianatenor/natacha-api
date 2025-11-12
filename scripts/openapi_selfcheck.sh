#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-}"
if [[ -z "$BASE" ]]; then
  echo "❌ BASE vacío"; exit 1
fi

say(){ echo -e "$@"; }

say "🔎 OpenAPI Selfcheck contra BASE=$BASE"
spec="$(curl -sf --max-time 15 "$BASE/openapi.json")" || { echo "🔴 No pude bajar openapi.json"; exit 1; }
paths="$(jq -r '.paths | keys[]?' <<<"$spec" || true)"

if [[ -z "$paths" ]]; then
  echo "🔴 openapi.json sin .paths"; exit 1
fi

has_path(){
  grep -qx "$1" <<<"$paths" >/dev/null 2>&1
}

# --- Checks robustos sin abortar el script ---
set +e  # evitamos que -e corte en verificaciones
need_ok=0
warn=0

# 1) /memory/add
if has_path "/memory/add"; then
  say "🟢 /memory/add en OpenAPI"; ((need_ok++))
else
  say "🟠 falta /memory/add en OpenAPI"; ((warn++))
fi

# 2) memory search (cualquiera de las dos)
if has_path "/memory/search" || has_path "/memory/v2/search"; then
  say "🟢 memory search en OpenAPI"; ((need_ok++))
else
  say "🟠 falta memory search en OpenAPI"; ((warn++))
fi

# 3) /v1/tasks/search
if has_path "/v1/tasks/search"; then
  say "🟢 /v1/tasks/search en OpenAPI"; ((need_ok++))
else
  say "🟠 falta /v1/tasks/search en OpenAPI"; ((warn++))
fi

set -e  # restauramos -e para el resto

say "ℹ️ total mínimos presentes: $need_ok (de 3) — warnings=$warn"

# criterio leniente por ahora: al menos 2/3
if (( need_ok < 2 )); then
  echo "🔴 OpenAPI insuficiente para contrato mínimo"; exit 1
fi

echo "✅ OpenAPI Selfcheck PASS (criterio leniente)"
