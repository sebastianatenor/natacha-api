#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://localhost:8080}"

check_http() {
  local url="$1"
  curl -sS -f -o /dev/null "$url"
}

check_openapi_has_path() {
  local path_regex="$1"
  curl -sS "$BASE/openapi.json" | jq -e --arg re "$path_regex" '
    (.paths | keys | map(select(test($re)))) | length > 0
  ' >/dev/null
}

check_memory_add() {
  curl -sS -f -X POST "$BASE/memory/add" \
    -H "Content-Type: application/json" \
    -d '{"summary":"health ping","detail":"","project":"Natacha","channel":"audit"}' >/dev/null
}

check_memory_search_filters() {
  curl -sS -f "$BASE/memory/search?project=Natacha&limit=3" >/dev/null
  curl -sS -f "$BASE/memory/search?channel=api&limit=3"   >/dev/null
}

# Intentar /memory/search_safe; devuelve:
#  0 si 200 OK
#  2 si 404 (no existe) -> activar fallback
#  1 si otro error
try_search_safe() {
  local code
  code="$(curl -s -o /dev/null -w '%{http_code}' -G "$BASE/memory/search_safe" \
    --data-urlencode "project=Natacha" \
    --data-urlencode "query=validación" \
    --data-urlencode "limit=3")"
  if [[ "$code" == "200" ]]; then
    return 0
  elif [[ "$code" == "404" ]]; then
    return 2
  else
    return 1
  fi
}

# Fallback a /memory/search (GET)
try_search_plain() {
  curl -sS -G -f "$BASE/memory/search" \
    --data-urlencode "project=Natacha" \
    --data-urlencode "query=validación" \
    --data-urlencode "limit=3" >/dev/null
}

run_memory_health() {
  echo "== Memory Health =="

  check_http "$BASE/health" && echo "🟢 /health OK" || { echo "🔴 /health FAIL"; return 1; }

  if check_openapi_has_path "/memory/search_safe"; then
    echo "🟢 OpenAPI expone /memory/search_safe"
  else
    echo "🟠 OpenAPI sin /memory/search_safe"
  fi

  check_memory_add && echo "🟢 /memory/add OK" || { echo "🔴 /memory/add FAIL"; return 1; }
  check_memory_search_filters && echo "🟢 /memory/search filtros OK" || { echo "🔴 /memory/search filtros FAIL"; return 1; }

  if try_search_safe; then
    echo "🟢 /memory/search_safe query OK"
  else
    rc=$?
    if [[ "$rc" == "2" ]]; then
      if try_search_plain; then
        echo "🟡 /memory/search_safe ausente; fallback a /memory/search OK"
      else
        echo "🔴 /memory/search fallback FAIL"
        return 1
      fi
    else
      echo "🔴 /memory/search_safe error inesperado"
      return 1
    fi
  fi

  echo "✅ Memory subsystem: HEALTHY"
}

run_memory_health
