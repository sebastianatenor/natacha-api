#!/usr/bin/env bash
# shellcheck shell=bash
. "$(dirname "$0")/../tools/canon_resolver.sh" || source tools/canon_resolver.sh
resolve_canon # exporta CANONICAL
#!/usr/bin/env bash
set -euo pipefail

SVC="natacha-api"; PROJ="asistente-sebastian"; REG="us-central1"
IMG="${1:-gcr.io/asistente-sebastian/natacha-api:fix-1762552879}"

echo "== 1) Backup previo =="
./scripts/backup_natacha.sh

echo "== 2) Deploy imagen =="
gcloud run deploy "$SVC" \
  --image "$IMG" \
  --region "$REG" \
  --project "$PROJ" \
  --labels=stage=canary,git_tag="$(git describe --tags --always --dirty)" \
  --quiet

URL=$(gcloud run services describe "$SVC" --project "$PROJ" --region "$REG" --format='value(status.url)')
echo "== 3) Healthcheck =="
curl -fsS "$URL/health" && echo
echo "✅ Deploy OK → $URL"
