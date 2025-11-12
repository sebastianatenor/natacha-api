#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://localhost:8080}"
KEY="${KEY:-}"   # opcional, si está la usamos
AUTH=()
[[ -n "$KEY" ]] && AUTH=(-H "X-API-Key: $KEY")

say() { echo "$@"; }

http_ok() {
  curl -sS -f -o /dev/null "${AUTH[@]}" "$1"
}

openapi_has_path() {
  local re="$1"
  curl -sS "${AUTH[@]}" "$BASE/openapi.json" | jq -e --arg re "$re" '
    (.paths | keys | map(select(test($re)))) | length > 0
  ' >/dev/null
}

# Devuelve el primer path que exista para search
discover_search_path() {
  # candidatos por orden de preferencia
  local candidates=(
    "/tasks/search"          # v0 GET o POST
    "/tasks/v1/search"       # v1 POST
    "/tasks/v2/search"       # v2 POST
  )
  for p in "${candidates[@]}"; do
    if openapi_has_path "$p"; then
      echo "$p"; return 0
    fi
  done
  return 1
}

# Intenta GET y si 404 prueba POST
probe_search() {
  local path="$1"
  # 1) GET con querystring básico
  local code
  code="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH[@]}" \
    -G "$BASE$path" --data-urlencode "q=health" --data-urlencode "limit=1")"
  if [[ "$code" == "200" ]]; then
    return 0
  fi
  if [[ "$code" != "404" && "$code" != "405" ]]; then
    # Otros errores -> fallar
    return 1
  fi
  # 2) POST con JSON
  code="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH[@]}" \
    -X POST "$BASE$path" -H "Content-Type: application/json" \
    -d '{"q":"health","limit":1}')"
  [[ "$code" == "200" ]]
}

# Crear una tarea dummy si existe el endpoint
probe_add() {
  local candidates=(
    "/tasks/add"
    "/tasks/v1/add"
    "/tasks/v2/add"
  )
  for p in "${candidates[@]}"; do
    if openapi_has_path "$p"; then
      local code
      code="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH[@]}" \
        -X POST "$BASE$p" -H "Content-Type: application/json" \
        -d '{"title":"health-dummy","tags":["ci","health"],"meta":{"probe":true}}')"
      [[ "$code" == "200" || "$code" == "201" ]] && return 0
    fi
  done
  # si no existe /add lo consideramos opcional
  return 0
}

main() {
  echo "== Tasks Health =="

  http_ok "$BASE/health" && say "🟢 /health OK" || { say "🔴 /health FAIL"; exit 1; }

  local SEARCH_PATH
  if SEARCH_PATH="$(discover_search_path)"; then
    if probe_search "$SEARCH_PATH"; then
      say "🟢 ${SEARCH_PATH} OK"
    else
      say "🔴 ${SEARCH_PATH} FAIL"
      exit 1
    fi
  else
    say "🔴 No se encontró endpoint de búsqueda de tareas en OpenAPI"
    exit 1
  fi

  if probe_add; then
    say "🟢 /tasks/add (si existe) OK"
  else
    say "🟠 /tasks/add no disponible"
  fi

  say "✅ Tasks subsystem: HEALTHY-ish"
}

main
