. "$(dirname "$0")/../tools/canon_resolver.sh" || source tools/canon_resolver.sh
resolve_canon # exporta CANONICAL
#!/usr/bin/env bash
set -euo pipefail
PROJ=${PROJ:-asistente-sebastian}
REG=${REG:-us-central1}
SVC=${SVC:-natacha-api}
CANON=${CANON:-${CANONICAL}}

echo "== status.url (puede variar) =="
gcloud run services describe "$SVC" --project "$PROJ" --region "$REG" \
  --format='value(status.url)'

echo "== Todas las URLs conocidas por Cloud Run =="
gcloud run services describe "$SVC" --project "$PROJ" --region "$REG" --format=json \
  | jq -r '.metadata.annotations["run.googleapis.com/urls"]'

echo "== OpenAPI server (debe ser la canónica) =="
curl -fsS "$CANON/openapi.v1.json" | jq -r '.servers[0].url'
