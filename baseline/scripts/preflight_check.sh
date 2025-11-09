#!/usr/bin/env bash
set -euo pipefail

PROJECT="${PROJECT:-asistente-sebastian}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-natacha-api}"

echo "== Preflight check =="
echo "Proyecto: $PROJECT | Región: $REGION | Servicio: $SERVICE"

# 1) Confirmar servicio
if ! gcloud run services describe "$SERVICE" --project "$PROJECT" --region "$REGION" >/dev/null 2>&1; then
  echo "❌ Servicio $SERVICE no existe en $REGION"
  exit 1
fi
echo "✅ Servicio existe"

# 2) Obtener URL y hacer healthcheck
URL=$(gcloud run services describe "$SERVICE" --project "$PROJECT" --region "$REGION" --format='value(status.url)')
echo "- URL: $URL"
echo "- /health:"
curl -sS "$URL/health" || echo "⚠️ No responde"

# 3) Mostrar revisiones y tráfico
echo
echo "== Revisiones y tráfico =="
gcloud run revisions list --project "$PROJECT" --region "$REGION" \
  --service "$SERVICE" --format="table(name,trafficPercent,creationTimestamp)"
