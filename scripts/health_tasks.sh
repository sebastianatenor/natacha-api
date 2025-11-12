#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://localhost:8080}"
KEY="${KEY:-}"   # opcional (usamos si está)
AUTH=()
[[ -n "$KEY" ]] && AUTH=(-H "X-API-Key: $KEY")

say() { echo "$@"; }

http_code() {
  # imprime solo el código HTTP
  curl -sS -o /dev/null -w '%{http_code}' "${AUTH[@]}" "$@"
}

fetch_openapi_paths() {
  # devuelve lista de paths (uno por línea); si falla, imprime vacío
  curl -sS "${AUTH[@]}" "$BASE/openapi.json" \
    | jq -r '.paths | keys[]?' 2>/dev/null || true
}

discover_search_paths() {
  # 1) preferir los que efectivamente existan en OpenAPI
  local paths; paths="$(fetch_openapi_paths || true)"
  if [[ -n "$paths" ]]; then
    # candidatos por regex amplios: tasks? + (opcional api/) + (vN/) + search
    # ejemplos válidos: /tasks/search, /task/search, /api/tasks/v1/search, /tasks/v2/search
    grep -E '^/(api/)?tasks?(/v[0-9]+)?/search$' <<<"$paths" || true
  fi
}

fallback_search_candidates() {
  cat <<EOF
/tasks/search
/tasks/v1/search
/tasks/v2/search
/task/search
/api/tasks/search
/api/tasks/v1/search
/api/tasks/v2/search
EOF
}

try_search_endpoint() {
  local ep="$1"
  # intentos en orden: GET con q, GET con query, POST con q, POST con query
  local code

  code="$(http_code -G "$BASE$ep" --data-urlencode "q=health" --data-urlencode "limit=1")"
  [[ "$code" == "200" ]] && { say "🟢 $ep GET(q) -> 200"; return 0; }
  [[ "$code" != "404" ]] && [[ "$code" != "405" ]] && say "ℹ️  $ep GET(q) -> $code"

  code="$(http_code -G "$BASE$ep" --data-urlencode "query=health" --data-urlencode "limit=1")"
  [[ "$code" == "200" ]] && { say "🟢 $ep GET(query) -> 200"; return 0; }
  [[ "$code" != "404" ]] && [[ "$code" != "405" ]] && say "ℹ️  $ep GET(query) -> $code"

  code="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH[@]}" \
            -X POST "$BASE$ep" -H "Content-Type: application/json" \
            -d '{"q":"health","limit":1}')" 
  [[ "$code" == "200" ]] && { say "🟢 $ep POST(q) -> 200"; return 0; }
  [[ "$code" != "404" ]] && [[ "$code" != "405" ]] && say "ℹ️  $ep POST(q) -> $code"

  code="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH[@]}" \
            -X POST "$BASE$ep" -H "Content-Type: application/json" \
            -d '{"query":"health","limit":1}')" 
  [[ "$code" == "200" ]] && { say "🟢 $ep POST(query) -> 200"; return 0; }
  [[ "$code" != "404" ]] && [[ "$code" != "405" ]] && say "ℹ️  $ep POST(query) -> $code"

  return 1
}

probe_add() {
  # Crear tarea dummy si existe algún /tasks.../add
  local paths; paths="$(fetch_openapi_paths || true)"
  local candidates=()
  if [[ -n "$paths" ]]; then
    while IFS= read -r p; do
      grep -qE '^/(api/)?tasks?(/v[0-9]+)?/add$' <<<"$p" && candidates+=("$p")
    done <<<"$paths"
  fi
  if [[ ${#candidates[@]} -eq 0 ]]; then
    # fallbacks razonables
    candidates=(/tasks/add /tasks/v1/add /tasks/v2/add /task/add /api/tasks/add)
  fi

  for ep in "${candidates[@]}"; do
    local code
    code="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH[@]}" \
      -X POST "$BASE$ep" -H "Content-Type: application/json" \
      -d '{"title":"health-dummy","tags":["ci","health"],"meta":{"probe":true}}')"
    if [[ "$code" == "200" || "$code" == "201" ]]; then
      say "🟢 $ep -> $code"
      return 0
    fi
    [[ "$code" != "404" ]] && [[ "$code" != "405" ]] && say "ℹ️  $ep -> $code"
  done

  # no lo consideramos crítico
  say "🟠 /tasks add endpoint no disponible"
  return 0
}

main() {
  echo "== Tasks Health =="

  local hc; hc="$(http_code "$BASE/health")"
  if [[ "$hc" != "200" ]]; then
    say "🔴 /health -> $hc"; exit 1
  fi
  say "🟢 /health OK"

  # 1) descubrir
  local discovered; discovered="$(discover_search_paths || true)"
  local tried=()

  if [[ -n "$discovered" ]]; then
    say "🔎 Paths de búsqueda detectados en OpenAPI:"
    echo "$discovered" | sed 's/^/   • /'
  else
    say "🟡 No se detectaron paths de búsqueda en OpenAPI, usando fallbacks."
  fi

  # 2) probar descubiertos primero, luego fallbacks
  while IFS= read -r ep; do
    [[ -z "$ep" ]] && continue
    tried+=("$ep")
    if try_search_endpoint "$ep"; then
      say "✅ Tasks search OK en: $ep"
      probe_add
      say "✅ Tasks subsystem: HEALTHY-ish"
      return 0
    fi
  done < <( (printf '%s\n' "$discovered"; fallback_search_candidates) | awk 'NF' | awk '!x[$0]++' )

  say "🔴 Ningún endpoint de búsqueda funcionó."
  say "   Probados:"
  printf '   - %s\n' "${tried[@]}"
  exit 1
}

main
