#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://localhost:8080}"

# Rutas declaradas en código (aproximación por grep)
code_paths=$(grep -RInE '@router\.(get|post)\\("(/[^"]+)"' routes routes/*.py routes/*/*.py 2>/dev/null \
  | sed -E 's/.*"((\/[^"]+))".*/\1/' \
  | sort -u)

# Rutas publicadas por OpenAPI
live_paths=$(curl -sS -f "$BASE/openapi.json" | jq -r '.paths | keys[]' | sort -u)

# Reporte
echo "== Router Wire Check =="
echo "En código (${BASE} no usado aquí):"
echo "$code_paths" | sed 's/^/  - /'
echo "En OpenAPI (${BASE}):"
echo "$live_paths" | sed 's/^/  - /'

# Comprobamos que lo mínimo esté publicado
must_have=(
  "/health"
  "/memory/add" "/memory/search"
  "/v1/tasks/search"
)

missing=()
for p in "${must_have[@]}"; do
  if ! echo "$live_paths" | grep -qx "$p"; then
    missing+=("$p")
  fi
done

if [[ ${#missing[@]} -gt 0 ]]; then
  echo "FALTANTES en OpenAPI: ${missing[*]}"
  exit 1
fi

echo "Router wiring: OK"
