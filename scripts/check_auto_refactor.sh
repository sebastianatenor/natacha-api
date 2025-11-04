#!/usr/bin/env bash
set -euo pipefail

SERVICE_URL="https://natacha-api-422255208682.us-central1.run.app"
PROJECT_ID="asistente-sebastian"

echo "== A) Sanity: debe existir UNA sola def de auto_plan_refactor =="
defs=$(grep -n "^def auto_plan_refactor" routes/auto_routes.py | wc -l | tr -d ' ')
echo "Encontradas: $defs"
if [ "$defs" != "1" ]; then
  echo "❌ Hay $defs definiciones; revisar routes/auto_routes.py"
  grep -n "^def auto_plan_refactor" routes/auto_routes.py || true
  exit 1
fi
echo "✅ OK"

echo
echo "== B) Invocar /auto/plan_refactor y capturar plan_id =="
resp=$(curl -s -X POST "$SERVICE_URL/auto/plan_refactor" \
  -H "Content-Type: application/json" \
  -d '{"goal":"limpiar duplicados de rutas"}')
echo "$resp" | jq '{status, plan_id, backups_found, task_created, message}'
plan_id=$(echo "$resp" | jq -r '.plan_id // empty')
if [ -z "$plan_id" ] || [ "$plan_id" = "null" ]; then
  echo "❌ No se obtuvo plan_id"
  exit 1
fi
echo "✅ plan_id: $plan_id"

echo
echo "== C) Últimas invocaciones en logs (Cloud Run) =="
gcloud logging read \
  'resource.type="cloud_run_revision"
   resource.labels.service_name="natacha-api"
   httpRequest.requestUrl:"/auto/plan_refactor"' \
  --project="$PROJECT_ID" \
  --limit=5 \
  --format="table(httpRequest.requestUrl,httpRequest.status,resource.labels.revision_name,receiveTimestamp)"

echo
echo "== D) Tareas canal=auto (top 5) =="
curl -s "$SERVICE_URL/tasks/search?limit=20" \
| jq '.items // . | map(select(.channel=="auto"))[:5]'
