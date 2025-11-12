#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://localhost:8080}"

# Descarga OpenAPI
json="$(curl -sS -f "$BASE/openapi.json")"

have() {
  echo "$json" | jq -e --arg p "$1" '.paths | has($p)' >/dev/null
}

ok=()
warn=()
fail=()

# Endpoints canónicos actuales
for p in "/health" \
         "/memory/add" "/memory/search" "/memory/v2/search" \
         "/v1/tasks/search" "/v1/tasks/add" "/v1/tasks/update" \
         "/ops/summary" "/ops/snapshots"; do
  if echo "$json" | jq -e --arg p "$p" '.paths | has($p)' >/dev/null; then
    ok+=("$p")
  else
    # /memory/search_safe hoy es opcional → warn si falta
    if [[ "$p" == "/memory/search_safe" ]]; then
      warn+=("$p")
    else
      # Para los ops, si alguno no existe no falla: algunos son informativos
      if [[ "$p" == /ops/* ]]; then
        warn+=("$p")
      else
        # /v1/tasks/add|update pueden faltar si aún no unificamos todo → warn
        if [[ "$p" == "/v1/tasks/add" || "$p" == "/v1/tasks/update" ]]; then
          warn+=("$p")
        else
          fail+=("$p")
        fi
      fi
    fi
  fi
done

echo "OpenAPI OK: ${ok[*]:-none}"
[[ ${#warn[@]} -gt 0 ]] && echo "OpenAPI WARN: ${warn[*]}"
if [[ ${#fail[@]} -gt 0 ]]; then
  echo "OpenAPI FAIL: ${fail[*]}"
  exit 1
fi
