#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://localhost:8080}"

check_http() {
  local url="$1"
  curl -sS -f -o /dev/null "$url"
}

check_json_key() {
  local url="$1" key="$2"
  curl -sS "$url" | jq -e "has($key)" >/dev/null
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
  curl -sS -f "$BASE/memory/search?channel=api&limit=3" >/dev/null
}

check_memory_search_safe_query() {
  curl -sS -G -f "$BASE/memory/search_safe" \
    --data-urlencode "project=Natacha" \
    --data-urlencode "query=validación" \
    --data-urlencode "limit=3" >/dev/null
}

run_memory_health() {
  echo "== Memory Health =="
  check_http "$BASE/health" && echo "🟢 /health OK" || { echo "🔴 /health FAIL"; return 1; }

  check_openapi_has_path "/memory/search_safe" && echo "🟢 OpenAPI expone /memory/search_safe" || echo "🟠 OpenAPI sin /memory/search_safe"

  check_memory_add && echo "🟢 /memory/add OK" || { echo "🔴 /memory/add FAIL"; return 1; }
  check_memory_search_filters && echo "🟢 /memory/search filtros OK" || { echo "🔴 /memory/search filtros FAIL"; return 1; }
  check_memory_search_safe_query && echo "🟢 /memory/search_safe query OK" || { echo "🔴 /memory/search_safe query FAIL"; return 1; }

  echo "✅ Memory subsystem: HEALTHY"
}

run_memory_health
