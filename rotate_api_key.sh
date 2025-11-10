#!/usr/bin/env bash
set -euo pipefail
PROJ="asistente-sebastian"
REG="us-central1"
SVC="natacha-api"
SECRET="NATACHA_API_KEY"
CANONICAL="https://natacha-api-422255208682.us-central1.run.app"

# 1) Nueva key sin salto de línea
NEW_KEY="natacha-secure-$(openssl rand -hex 8)"
printf %s "$NEW_KEY" | gcloud secrets versions add "$SECRET" --data-file=- --project "$PROJ" >/dev/null

# 2) Forzar servicio a leer 'latest'
gcloud run services update "$SVC" \
  --project "$PROJ" \
  --region "$REG" \
  --set-secrets API_KEY=${SECRET}:latest >/dev/null

# 3) Pensamiento (auditoría)
KEY="$(gcloud secrets versions access latest --secret "$SECRET" --project "$PROJ" | tr -d '\r\n')"
curl -sS -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -X POST "$CANONICAL/think" \
  --data "$(jq -n --arg msg "API_KEY rotated & service updated" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
               '{input: ($msg+" @ "+$ts), topic:"ai-core", tags:["security","rotation","auto"]}')" >/dev/null
echo "✅ Rotation OK"
