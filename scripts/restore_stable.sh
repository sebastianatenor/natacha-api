. "$(dirname "$0")/../tools/canon_resolver.sh" || source tools/canon_resolver.sh
resolve_canon # exporta CANONICAL
#!/usr/bin/env bash
set -euo pipefail
SVC="natacha-api"; PROJ="asistente-sebastian"; REG="us-central1"
IMG="gcr.io/$PROJ/natacha-api:stable"

echo "== Desplegando imagen estable =="
gcloud run deploy "$SVC" \
  --image "$IMG" \
  --region "$REG" \
  --project "$PROJ" \
  --labels=stage=stable,rollback=manual \
  --quiet

echo "== Salud =="
URL=$(gcloud run services describe "$SVC" --project "$PROJ" --region "$REG" --format='value(status.url)')
curl -fsS "$URL/health" && echo
echo "✅ Rollback a :stable completado → $URL"
