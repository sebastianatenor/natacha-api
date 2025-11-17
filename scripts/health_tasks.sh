#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://localhost:8000}"
USER_ID="${1:-sebastian}"

echo "Using BASE=$BASE"
echo
echo "== Tasks Health =="

check_json() {
  local resp="$1"
  echo "$resp" | jq empty >/dev/null 2>&1
}

# 1) /health
echo "🔎 Probing /health ..."
health_resp="$(curl -sS "$BASE/health" || true)"

if check_json "$health_resp" && echo "$health_resp" | jq -e '.status == "ok"' >/dev/null 2>&1; then
  echo "🟢 /health OK"
else
  echo "🔴 /health FAIL"
  echo "Response (non-JSON or invalid):"
  echo "$health_resp"
  exit 1
fi

# 2) Crear tarea de prueba vía /v1/tasks/add
echo
echo "🔎 Creando tarea de prueba en /v1/tasks/add ..."

payload="$(cat <<JSON
{
  "user_id": "$USER_ID",
  "title": "Healthcheck task",
  "detail": "Tarea creada por scripts/health_tasks.sh",
  "project": "Natacha",
  "channel": "health"
}
JSON
)"

create_resp="$(curl -sS -X POST "$BASE/v1/tasks/add" \
  -H "Content-Type: application/json" \
  -d "$payload" || true)"

if check_json "$create_resp"; then
  echo "$create_resp" | jq . || true
else
  echo "⚠️ Invalid or non-JSON response from /v1/tasks/add:"
  echo "$create_resp"
  exit 1
fi

TASK_ID="$(echo "$create_resp" | jq -r '.id // .task.id // .stored.id // empty')"

if [[ -z "$TASK_ID" || "$TASK_ID" == "null" ]]; then
  if echo "$create_resp" | jq -e '.status == "ok"' >/dev/null 2>&1; then
    echo "🟠 /v1/tasks/add OK (legacy, sin id devuelto)"
    echo "✅ Tasks subsystem: HEALTHY (legacy add-only)"
    exit 0
  else
    echo "🔴 /v1/tasks/add FAIL – no se pudo obtener id de la tarea"
    exit 1
  fi
fi

echo "🟢 /v1/tasks/add OK (id=$TASK_ID)"

# 3) Marcarla como done vía /v1/tasks/update
echo
echo "🔎 Marcando tarea como done en /v1/tasks/update ..."

update_payload="$(cat <<JSON
{
  "user_id": "$USER_ID",
  "task_id": "$TASK_ID",
  "state": "done"
}
JSON
)"

update_resp="$(curl -sS -X POST "$BASE/v1/tasks/update" \
  -H "Content-Type: application/json" \
  -d "$update_payload" || true)"

if check_json "$update_resp"; then
  echo "$update_resp" | jq . || true
else
  echo "⚠️ Invalid or non-JSON response from /v1/tasks/update:"
  echo "$update_resp"
  exit 1
fi

STATE="$(echo "$update_resp" | jq -r '.state // .task.state // empty')"

if [[ "$STATE" == "done" ]]; then
  echo "🟢 /v1/tasks/update OK (state=done)"
else
  echo "🟠 /v1/tasks/update devolvió algo raro (state=$STATE)"
fi

echo
echo "✅ Tasks subsystem: HEALTHY"
