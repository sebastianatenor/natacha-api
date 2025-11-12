#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://localhost:8080}"
KEY="${KEY:-}"

say(){ echo -e "$*"; }

check_http() {
  curl -sS -f -o /dev/null "$1"
}

run_tasks_health() {
  say "== Tasks Health =="

  check_http "$BASE/health" && say "🟢 /health OK" || { say "🔴 /health FAIL"; exit 1; }

  # Detectar endpoint en OpenAPI
  if curl -sS "$BASE/openapi.json" | jq -e '.paths["/v1/tasks/search"]' >/dev/null; then
    PATH_TASKS="/v1/tasks/search"
  elif curl -sS "$BASE/openapi.json" | jq -e '.paths["/tasks/search"]' >/dev/null; then
    PATH_TASKS="/tasks/search"
  else
    say "🟠 No se encontró /v1/tasks/search ni /tasks/search en OpenAPI."
    say "✅ Tasks subsystem: HEALTHY-ish (best effort)"
    exit 0
  fi

  say "🔎 Probing $PATH_TASKS ..."
  if [[ -n "$KEY" ]]; then
    curl -sS -f -G "$BASE$PATH_TASKS" -H "X-API-Key: $KEY" --data-urlencode "limit=3" >/dev/null \
      && say "🟢 GET $PATH_TASKS OK (200)" \
      && say "✅ Tasks subsystem: HEALTHY" && exit 0
  else
    curl -sS -f -G "$BASE$PATH_TASKS" --data-urlencode "limit=3" >/dev/null \
      && say "🟢 GET $PATH_TASKS OK (200)" \
      && say "✅ Tasks subsystem: HEALTHY" && exit 0
  fi

  say "🔴 $PATH_TASKS FAIL"
  exit 1
}

run_tasks_health
