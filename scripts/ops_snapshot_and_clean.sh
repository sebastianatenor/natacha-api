#!/usr/bin/env bash
set -euo pipefail

# ==== CONFIG ====
SERVICE="natacha-api"
PROJECT_ID="asistente-sebastian"
REGION="us-central1"
GOOD_URL="https://natacha-api-422255208682.us-central1.run.app"
KEEP_READY=5   # cuántas revisiones Ready antiguas conservar (además de serving y latestCreated)

# ==== Helpers ====
log(){ printf "%s %s\n" "$(date -u +'%FT%TZ')" "$*"; }
g(){ gcloud "$@" --project="${PROJECT_ID}"; }

# ==== A) Snapshot de estado (serving, latest, imagen) ====
log "📸 Snapshot de servicio"
SERVING_REV="$(g run services describe "${SERVICE}" --region="${REGION}" --format='value(status.traffic[0].revisionName)')"
LATEST_CREATED="$(g run services describe "${SERVICE}" --region="${REGION}" --format='value(status.latestCreatedRevisionName)')"
IMG_DIGEST="$(g run revisions describe "${SERVING_REV}" --region="${REGION}" --format='value(spec.containers[0].image)')"
SERVICE_URL_CUR="$(g run services describe "${SERVICE}" --region="${REGION}" --format='value(status.url)')"

log "• URL actual:              ${SERVICE_URL_CUR}"
log "• Revisión en producción:  ${SERVING_REV}"
log "• Última creada:           ${LATEST_CREATED}"
log "• Imagen en uso:           ${IMG_DIGEST}"

# ==== B) Sanidad de URL (forzar formato project-number.run.app) ====
log "🔗 Asegurando URL por defecto (project-number.run.app)"
g run services update "${SERVICE}" --region="${REGION}" --default-url || true

# ==== C) Pin de imagen (opcional, sin cambiar tráfico) ====
log "📌 Pinneando imagen actual (sin mover tráfico)"
g run deploy "${SERVICE}" --region="${REGION}" --image "${IMG_DIGEST}" --no-traffic --allow-unauthenticated

# Reafirmar 100% en la revisión SERVING (por si algún cambio tocó el split)
log "🚦 Manteniendo 100% tráfico en ${SERVING_REV}"
g run services update-traffic "${SERVICE}" --region="${REGION}" --to-revisions="${SERVING_REV}=100"

# ==== D) Health checks de OPS ====
log "🩺 Health checks /ops"
curl -fsS "${GOOD_URL}/ops/ping"          | jq . >/dev/null && log "• /ops/ping OK"
curl -fsS "${GOOD_URL}/ops/smart_health"  | jq . >/dev/null && log "• /ops/smart_health OK"
curl -fsS "${GOOD_URL}/ops/version"       | jq . >/dev/null && log "• /ops/version OK"

# ==== E) Limpiar revisiones NotReady (excepto la latestCreated) ====
log "🧹 Borrando NotReady (excepto latestCreated)"
NOT_READY_LIST="$(g run revisions list --region="${REGION}" --service="${SERVICE}" \
  --filter='status.conditions.type=Ready AND status.conditions.status=False' \
  --format='value(name)')"

for R in ${NOT_READY_LIST:-}; do
  if [[ "$R" == "$LATEST_CREATED" ]]; then
    log "⛔ Protegida (latestCreated): $R"
  else
    log "🧽 Deleting NotReady $R"
    g run revisions delete "$R" --region="${REGION}" --quiet || true
  fi
done

# ==== F) Mantener solo N Ready antiguas (además de serving y latestCreated) ====
log "📦 Limpiando Ready antiguas (conservar ${KEEP_READY}, +serving +latestCreated)"
READY_LIST="$(g run revisions list --region="${REGION}" --service="${SERVICE}" \
  --filter='status.conditions.type=Ready AND status.conditions.status=True' \
  --format='value(name)')"

COUNT=0
for R in ${READY_LIST:-}; do
  if [[ "$R" == "$SERVING_REV" || "$R" == "$LATEST_CREATED" ]]; then
    log "🛡️ Keep (protegida) $R"
    continue
  fi
  COUNT=$((COUNT+1))
  if (( COUNT <= KEEP_READY )); then
    log "✅ Keep $R"
  else
    log "🗑️ Delete old Ready $R"
    g run revisions delete "$R" --region="${REGION}" --quiet || true
  fi
done

# ==== G) End ====
log "✅ Listo. Estado final:"
g run revisions list --region="${REGION}" --service="${SERVICE}" \
  --format='table(name,status.conditions[0].type,status.conditions[0].status,creationTimestamp)'
