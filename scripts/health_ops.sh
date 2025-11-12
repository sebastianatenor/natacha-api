#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://localhost:8080}"

check_http() { curl -fsS -o /dev/null "$1"; }

echo "== Ops Health =="

check_http "$BASE/health" && echo "🟢 /health OK" || { echo "🔴 /health FAIL"; exit 1; }

# OpenAPI presente
spec=$(curl -fsS "$BASE/openapi.json") || { echo "🔴 openapi FAIL"; exit 1; }
echo "🟢 OpenAPI OK"

# Heurística: ¿hay paths que contengan '/ops'?
if echo "$spec" | jq -e '.paths | to_entries | any(.key | contains("/ops"))' >/dev/null; then
  echo "🟢 Ops endpoints detectados en OpenAPI"
else
  echo "🟡 No se detectan /ops en OpenAPI (solo info)"
fi

echo "✅ Ops: HEALTHY (básico)"
