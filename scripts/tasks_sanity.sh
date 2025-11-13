#!/usr/bin/env bash
set -euo pipefail

SERVICE_URL="${SERVICE_URL:-https://natacha-api-422255208682.us-central1.run.app}"
USER_ID="${1:-sebastian}"

echo "== A) Health =="
curl -s "$SERVICE_URL/health" | jq .

echo
echo "== B) Crear tarea de sanity =="
CREATE_RESP=$(curl -s -X POST "$SERVICE_URL/tasks/add" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"title\": \"Sanity task auto\",
    \"detail\": \"Tarea creada por scripts/tasks_sanity.sh\",
    \"project\": \"LLVC\",
    \"channel\": \"gpt-chat\"
  }")

echo "$CREATE_RESP" | jq .
TASK_ID=$(echo "$CREATE_RESP" | jq -r '.task.id // .id // empty')

if [ -z "$TASK_ID" ] || [ "$TASK_ID" = "null" ]; then
  echo "❌ No pude extraer TASK_ID de la respuesta"
  exit 1
fi

echo
echo "TASK_ID detectado: $TASK_ID"

echo
echo "== C) Marcar tarea como done =="
curl -s -X POST "$SERVICE_URL/tasks/update" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"id\": \"$TASK_ID\",
    \"state\": \"done\"
  }" | jq .

echo
echo "== D) Verificar desde /tasks/list =="
curl -s "$SERVICE_URL/tasks/list?user_id=$USER_ID" | \
  jq ".items[] | select(.id==\"$TASK_ID\")"

echo
echo "✅ Sanity de tasks finalizado"
