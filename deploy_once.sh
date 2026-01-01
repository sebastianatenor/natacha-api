#!/usr/bin/env bash
set -e

echo "🚀 Natacha — Deploy Once (canonical)"

PROJECT="asistente-sebastian"
REGION="us-central1"
SERVICE="natacha-api"

echo "▶️ Preflight local"
source .venv_deploy/bin/activate
python3 - << 'PY'
from service_main import app
paths = app.openapi()["paths"].keys()
assert "/agent/interact" in paths
print("✔ preflight OK")
PY

echo "▶️ Deploying to Cloud Run"
gcloud run deploy $SERVICE \
  --source . \
  --region $REGION \
  --project $PROJECT \
  --quiet

echo "✅ Deploy completo"
