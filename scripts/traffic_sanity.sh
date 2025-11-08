#!/usr/bin/env bash
# shellcheck shell=bash
. "$(dirname "$0")/../tools/canon_resolver.sh" || source tools/canon_resolver.sh
resolve_canon # exporta CANONICAL
#!/usr/bin/env bash
set -euo pipefail
PROJ=${PROJ:-asistente-sebastian}
REG=${REG:-us-central1}
SVC=${SVC:-natacha-api}

CURR=$(gcloud run services describe "$SVC" --project "$PROJ" --region "$REG" --format=json)

PINNED=$(echo "$CURR" | jq '[.spec.traffic[] | has("revisionName")] | any')
if [ "$PINNED" = "true" ]; then
  echo "⚠️ Detectado pin a revisionName -> corrigiendo a --to-latest"
  gcloud run services update-traffic "$SVC" --project "$PROJ" --region "$REG" --to-latest
fi

SERVICE_URL=$(echo "$CURR" | jq -r '.status.url')
gcloud run services update "$SVC" --project "$PROJ" --region "$REG" \
  --set-env-vars "OPENAPI_PUBLIC_URL=${SERVICE_URL}" --no-traffic
echo "✅ Sanity OK: to-latest y OPENAPI_PUBLIC_URL=$SERVICE_URL"
