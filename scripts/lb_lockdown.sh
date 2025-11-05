#!/usr/bin/env bash
set -euo pipefail
PROJ=${PROJ:-asistente-sebastian}
REG=${REG:-us-central1}
SVC=${SVC:-natacha-api}
DOMAIN=${DOMAIN:?export DOMAIN antes de ejecutar}

echo "== DNS check =="
dig +short $DOMAIN

echo "== Cert status =="
gcloud compute ssl-certificates describe cert-${SVC} --project $PROJ \
  --format='get(managed.status,managed.domains)'

echo ">> Si el certificado no está ACTIVE, esperá y reintentá"
read -p "¿El cert está ACTIVE? (y/N) " yn
[[ "${yn,,}" == "y" ]] || { echo "Abortado"; exit 1; }

echo "== Lockdown ingress =="
gcloud run services update $SVC --project $PROJ --region $REG \
  --ingress internal-and-cloud-load-balancing

echo "== Public OpenAPI server =="
gcloud run services update $SVC --project $PROJ --region $REG \
  --set-env-vars OPENAPI_PUBLIC_URL="https://$DOMAIN" --no-traffic

echo "== Smoke =="
curl -I https://$DOMAIN/__alive || true
curl -fsS https://$DOMAIN/openapi.v1.json | jq -r '.servers[].url' || true
curl -I https://natacha-api-mkwskljrhq-uc.a.run.app || true

echo "✅ Listo."
