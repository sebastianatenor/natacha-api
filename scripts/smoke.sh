#!/usr/bin/env bash
set -euo pipefail
CANONICAL="https://natacha-api-422255208682.us-central1.run.app"
KEY="$(gcloud secrets versions access latest --secret NATACHA_API_KEY --project asistente-sebastian | tr -d '\r\n')"

echo "== /health =="
curl -fsS "$CANONICAL/health" >/dev/null && echo "OK"

echo "== 401 sin API key =="
code=$(curl -s -o /dev/null -w "%{http_code}\n" "$CANONICAL/memory/search"); echo "$code"; [ "$code" = "401" ]

echo "== 200 con API key (X-API-Key) =="
curl -fsS -H "X-API-Key: $KEY" "$CANONICAL/context?topic=ai-core&limit=1" | jq '.count'

echo "== 200 con Bearer =="
curl -fsS -H "Authorization: Bearer $KEY" "$CANONICAL/context?topic=ai-core&limit=1" | jq '.count'
echo "✅ Smoke OK"
