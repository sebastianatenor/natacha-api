#!/bin/bash
set -e

SERVICE="$1"
PROJECT_ID="asistente-sebastian"
REGION="us-central1"

if [ -z "$SERVICE" ]; then
  echo "❌ Debes indicar el servicio. Ejemplo:"
  echo "   bash deploy_safe.sh natacha-health-monitor"
  exit 1
fi

echo "============================================="
echo "🧠 Natacha CloudRun — despliegue seguro iniciado"
echo "Servicio: $SERVICE | Proyecto: $PROJECT_ID"
echo "============================================="

# Detectar revisión actual
echo ""
echo "📦 Obteniendo revisión actual..."
CURRENT_REV=$(gcloud run services describe "$SERVICE" \
  --project="$PROJECT_ID" --region="$REGION" \
  --format="value(status.latestReadyRevisionName)" || echo "none")

echo "🕓 Revisión actual: ${CURRENT_REV:-none}"
echo ""

# Compilar imagen
echo "🔧 Iniciando compilación..."
gcloud builds submit --tag "gcr.io/$PROJECT_ID/$SERVICE" .

echo ""
echo "☁️ Desplegando en Cloud Run..."
gcloud run deploy "$SERVICE" \
  --image "gcr.io/$PROJECT_ID/$SERVICE" \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --platform managed \
  --allow-unauthenticated

URL=$(gcloud run services describe "$SERVICE" \
  --region="$REGION" --project="$PROJECT_ID" \
  --format="value(status.url)")

echo ""
echo "✅ Despliegue completado."
echo "🌐 URL del servicio: $URL"
echo ""

# Healthcheck dinámico
HEALTHCHECK="$URL"
if [[ "$SERVICE" == "natacha-api" ]]; then
  HEALTHCHECK="$URL/ops/force_learn"
elif [[ "$SERVICE" == "natacha-health-monitor" ]]; then
  HEALTHCHECK="$URL/"
fi

echo "🩺 Verificando estado del servicio..."
echo "🔍 Ejecutando prueba: $HEALTHCHECK"

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTHCHECK")

if [[ "$HTTP_CODE" == "200" ]]; then
  echo "✅ Prueba de salud exitosa (HTTP 200)"
else
  echo "❌ La API devolvió un código inesperado: $HTTP_CODE"
  if [ "$CURRENT_REV" != "none" ]; then
    echo "↩️  Restaurando la revisión anterior..."
    gcloud run services update-traffic "$SERVICE" \
      --to-revisions "$CURRENT_REV=100" \
      --region="$REGION" --project="$PROJECT_ID"
    echo "✅ Rollback completado."
  else
    echo "⚠️ No se encontró revisión anterior, rollback omitido."
  fi
fi
