#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://localhost:8080}"

check_http() { curl -fsS -o /dev/null "$1"; }

echo "== Tasks Health =="

# 1) /health vivo
check_http "$BASE/health" && echo "🟢 /health OK" || { echo "🔴 /health FAIL"; exit 1; }

# 2) /tasks/search responde 200 y JSON (array u objeto)
if out=$(curl -fsS "$BASE/tasks/search"); then
  echo "🟢 /tasks/search OK"
else
  echo "🔴 /tasks/search FAIL"; exit 1
fi

# 3) Intento opcional de alta "benigna" (no crítico)
#    Si tu /tasks/add exige campos, ajusta acá. Si falla, solo advierte.
payload='{"summary":"healthcheck task","project":"Natacha","channel":"health","visibility":"equipo","state":"vigente"}'
if curl -fsS -X POST "$BASE/tasks/add" -H "Content-Type: application/json" -d "$payload" >/dev/null; then
  echo "🟢 /tasks/add OK (dummy)"
else
  echo "🟡 /tasks/add no aceptó el dummy (no crítico)"
fi

echo "✅ Tasks subsystem: HEALTHY-ish"
