#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-}"
if [[ -z "$BASE" ]]; then
  echo "❌ BASE vacío"; exit 1
fi

say(){ echo -e "$@"; }

say "🔎 OpenAPI Selfcheck contra BASE=$BASE"
spec="$(curl -sf --max-time 15 "$BASE/openapi.json")"
paths="$(jq -r '.paths | keys[]?' <<<"$spec" || true)"

if [[ -z "$paths" ]]; then
  echo "🔴 openapi.json sin .paths"; exit 1
fi

has_path(){
  grep -qx "$1" <<<"$paths"
}

warn=0; req=0

# Requisitos mínimos (según lo que realmente expone hoy tu servicio)
need_ok=0

# /memory/add
if has_path "/memory/add"; then say "🟢 /memory/add en OpenAPI"; ((need_ok++)); else say "🟠 falta /memory/add en OpenAPI"; ((warn++)); fi
# /memory/search (o variantes v2/smart si las querés exigir más adelante)
if has_path "/memory/search" || has_path "/memory/v2/search"; then say "🟢 memory search en OpenAPI"; ((need_ok++)); else say "🟠 falta memory search en OpenAPI"; ((warn++)); fi
# /v1/tasks/search (tu canónico actual)
if has_path "/v1/tasks/search"; then say "🟢 /v1/tasks/search en OpenAPI"; ((need_ok++)); else say "🟠 falta /v1/tasks/search en OpenAPI"; ((warn++)); fi

say "ℹ️ total mínimos presentes: $need_ok (de 3) — warnings=$warn"
# Aprobamos si al menos 2/3 están — más estricto lo ponemos luego cuando estabilicemos contrato
if (( need_ok < 2 )); then
  echo "🔴 OpenAPI insuficiente para contrato mínimo"; exit 1
fi

echo "✅ OpenAPI Selfcheck PASS (criterio leniente)"
