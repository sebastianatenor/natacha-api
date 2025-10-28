#!/bin/bash
set -e

PROJECT="asistente-sebastian"
REGION="us-central1"
SERVICE="natacha-api"
IMAGE="gcr.io/$PROJECT/$SERVICE"

echo "🚀 Construyendo imagen para $SERVICE..."
gcloud builds submit --tag $IMAGE

echo "☁️ Desplegando en Cloud Run..."
gcloud run deploy $SERVICE \
  --image $IMAGE \
  --region=$REGION \
  --project=$PROJECT \
  --set-secrets WHATSAPP_TOKEN=META_WHATSAPP_TOKEN:latest \
  --allow-unauthenticated

echo "✅ Despliegue completo."
echo "🌐 URL del servicio:"
gcloud run services describe $SERVICE \
  --region=$REGION \
  --project=$PROJECT \
  --format="value(status.url)"
