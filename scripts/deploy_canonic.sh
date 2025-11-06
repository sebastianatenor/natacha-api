#!/usr/bin/env bash
set -euo pipefail

### 0) Config fija
gcloud config set project asistente-sebastian >/dev/null
gcloud config set run/region us-central1 >/dev/null
gcloud config set run/platform managed >/dev/null

### 1) Vars base
export SVC="natacha-api"
export PROJ="$(gcloud config get-value project)"
export REG="$(gcloud config get-value run/region)"
export PROJNUM="$(gcloud projects describe "$PROJ" --format='value(projectNumber)')"
export URL_CANON="https://${SVC}-${PROJNUM}.${REG}.run.app"  # CANONICAL_OK

echo "== Deploy a canónica =="
echo "Proyecto : $PROJ"
echo "Región   : $REG"
echo "Servicio : $SVC"
echo "Canónica : $URL_CANON"
echo

### 2) Imagen actual del servicio (reusa la última imagen buena)
IMG="$(gcloud run services describe "$SVC" --region "$REG" \
        --format='value(spec.template.spec.containers[0].image)')"
echo "Imagen    : $IMG"
echo

### 3) Deploy robusto (uvicorn explícito + limpia envs viejas)
gcloud run deploy "$SVC" \
  --region "$REG" \
  --image "$IMG" \
  --execution-environment gen2 --ingress all \
  --cpu 1 --memory 512Mi --concurrency 10 \
  --timeout 300 --min-instances 1 --cpu-boost \
  --command=python \
  --args=-m,uvicorn,service_main:app,--host,0.0.0.0,--port,8080 \
  --update-env-vars OPENAPI_PUBLIC_URL="$URL_CANON",REV_BUMP=$(date +%s) \
  --remove-env-vars=APP_MODULE,GUNICORN_CMD_ARGS,STARTUP_CMD

### 4) Smoke ONLY canónica
echo
echo "== Smoke canónica =="
fail=0
for p in /__alive /openapi.v1.json /openapi.json /actions/catalog /auto/list_repo; do
  code="$(curl -s -o /dev/null -w "%{http_code}" "$URL_CANON$p")"
  printf "%-18s %s\n" "$p" "$code"
  [[ "$code" == "200" ]] || fail=1
done
srv="$(curl -s "$URL_CANON/openapi.v1.json" | jq -r '.servers[0].url' || true)"
echo "servers[0].url => ${srv:-<null>}"
[[ "${srv:-}" == "$URL_CANON" ]] || fail=1

### 5) Snapshot de logs (últimos 5 min)
echo
REV_LAST="$(gcloud run services describe "$SVC" --region "$REG" \
  --format='value(status.latestCreatedRevisionName)')"
echo "== Logs (rev $REV_LAST, 5m) =="
gcloud logging read \
  'resource.type="cloud_run_revision"
   resource.labels.service_name="'"$SVC"'"
   resource.labels.revision_name="'"$REV_LAST"'"' \
  --freshness="5m" --limit=50 --format="value(textPayload)" || true

### 6) Actualizar REGISTRY.md
echo
echo "== Actualizando REGISTRY.md =="
DIGEST=$(echo "$IMG" | sed -E 's/.*@//')
DATE=$(date '+%Y-%m-%d %H:%M:%S')
cat > REGISTRY.md <<EOF
# Natacha API Deployment Registry

**Fecha:** $DATE  
**Proyecto:** $PROJ  
**Región:** $REG  
**Servicio:** $SVC  

- URL canónica: $URL_CANON  
- Última revisión: $REV_LAST  
- Imagen: $IMG  
- Digest: $DIGEST  

✅ Estado: OK  
EOF
echo "Archivo REGISTRY.md actualizado ✅"

echo
if [[ $fail -eq 0 ]]; then
  echo "✅ Deploy OK y canónica saludable: $URL_CANON"
else
  echo "❌ Smoke/servers[0].url falló. Revisar logs arriba." >&2
  exit 1
fi
