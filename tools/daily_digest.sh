#!/bin/zsh
set -eo pipefail
PROJECT=${PROJECT:-asistente-sebastian}
REGION=${REGION:-us-central1}
LOCATION=${LOCATION:-us-central1}
PROJECT=${PROJECT:-asistente-sebastian}
REGION=${REGION:-us-central1}
LOCATION=${LOCATION:-us-central1}
PROJECT=${PROJECT:-asistente-sebastian}
REGION=${REGION:-us-central1}
LOCATION=${LOCATION:-us-central1}

# Último snapshot
S="$(ls -1dt "$HOME/Projects/natacha-api/infra_snapshots"/20*Z | head -n1)"
OUT_MD="$HOME/Projects/natacha-api/infra_snapshots/latest.md"

# Helpers
val_or_nd() { [ -s "$1" ] && echo "sí" || echo "no"; }

# Conteos
svc_count=$(jq 'length' "$S/run.services.json" 2>/dev/null || echo 0)
job_count=$(jq 'length' "$S/sched.jobs.json" 2>/dev/null || echo 0)
pol_count=$(jq 'length' "$S/mon.policies.json" 2>/dev/null || echo 0)
log_metrics=$(val_or_nd "$S/log.metrics.json")

# Cabecera
{
  echo "# Natacha – Daily Digest ($(basename "$S" | sed 's/[^0-9T]//g'))"
  echo
  echo "- Proyecto: asistente-sebastian"
  echo "- Región: us-central1"
  echo "- Host: $(tr '\n' ' ' < "$S/sys.uname" 2>/dev/null | cut -c1-200)"
  echo
  echo "## Resumen rápido"
  echo
  echo "- Servicios Cloud Run: $svc_count"
  echo "- Jobs Scheduler: $job_count"
  echo "- Métricas Logging: $log_metrics"
  echo "- Políticas Monitoring: $pol_count"
  echo
  echo "## Servicios Cloud Run"
  if [ -s "$S/run.services.json" ]; then
    jq -r '.[0:15][] | "- \(.metadata.name) -> \(.status.url // "s/n")"' "$S/run.services.json"
  else
    echo "_Sin datos_"
  fi
  echo
  echo "## Scheduler (jobs)"
  if [ -s "$S/sched.jobs.json" ]; then
    jq -r '.[0:15][] | "- \(.name | split("/")[-1]) @ \(.schedule) [\(.state)]"' "$S/sched.jobs.json"
  else
    echo "_Sin datos_"
  fi
  echo
  echo "## Últimos logs (-1h)"
  if [ -s "$S/log.sample.json" ]; then
    # Muestra hasta 20 líneas de logs en formato simple si existe
    jq -r '.[0:20][] | "- \(.timestamp // .ts // "n/a")  \(.resource.labels.service_name // .service // "n/a"): \((.textPayload // .message // .jsonPayload // .protoPayload // "")|tostring|gsub("\\r?\\n"; " ") | .[0:240])"' "$S/log.sample.json" || echo "_Sin datos_"
  else
    echo "_Sin datos_"
  fi
  echo
  echo "## IAM (Run invoker/viewer)"
  echo
  echo "### roles/run.invoker"
  if [ -s "$S/iam.run_invokers.json" ]; then
    jq -r '.[] | "    \(.role)  \(.members[]?)"' "$S/iam.run_invokers.json"
  else
    echo "_Sin datos_"
  fi
  echo
  echo "### roles/run.viewer"
  if [ -s "$S/iam.run_viewers.json" ]; then
    jq -r '.[] | "    \(.role)  \(.members[]?)"' "$S/iam.run_viewers.json"
  else
    echo "_Sin datos_"
  fi
  echo
  echo "## Secrets (names)"
  if [ -s "$S/secrets.json" ]; then
    jq -r '.[] | "- \(.name)"' "$S/secrets.json"
  else
    echo "_Sin datos_"
  fi
} > "$OUT_MD"

echo "✅ Digest generado: $OUT_MD"

# === Scheduler: última ejecución de run-auto-heal ===
{
  echo
  echo "## Scheduler (última ejecución de run-auto-heal)"
  LAST_JSON="$(gcloud logging read \
    'resource.type="cloud_run_revision" AND resource.labels.service_name="natacha-health-monitor" AND httpRequest.requestUrl:"/auto_heal"' \
    --project="$PROJECT" --limit=1 --order=desc --format=json 2>/dev/null || echo '[]')"

  if [ "$(echo "$LAST_JSON" | jq 'length')" -gt 0 ]; then
    TS="$(echo "$LAST_JSON" | jq -r '.[0].timestamp // .[0].receiveTimestamp // "n/a"')"
    ST="$(echo "$LAST_JSON" | jq -r '.[0].httpRequest.status // "n/a"')"
    URL="$(echo "$LAST_JSON" | jq -r '.[0].httpRequest.requestUrl // "n/a"')"
    PATH_ONLY="$(echo "$URL" | sed -E 's#https?://[^/]+##')"
    echo "- Último intento: $TS"
    echo "- Resultado: HTTP $ST"
    echo "- Endpoint: ${PATH_ONLY:-/auto_heal}"
  else
    echo "_Sin datos recientes del job run-auto-heal_"
  fi
} >> "$OUT_MD"

# ===== Scheduler summary (run-auto-heal) =====
{
  echo
  echo "## Scheduler (run-auto-heal)"

  JOB_ID="run-auto-heal"

  # Último intento (desde Cloud Run logs del servicio health-monitor filtrando /auto_heal)
  LAST_TS="$(gcloud logging read \
    'resource.type="cloud_run_revision" AND resource.labels.service_name="natacha-health-monitor" AND httpRequest.requestUrl:"/auto_heal"' \
    --project="${PROJECT}" --limit=1 --order=desc \
    --format='value(timestamp)' 2>/dev/null || true)"

  LAST_CODE="$(gcloud logging read \
    'resource.type="cloud_run_revision" AND resource.labels.service_name="natacha-health-monitor" AND httpRequest.requestUrl:"/auto_heal"' \
    --project="${PROJECT}" --limit=1 --order=desc \
    --format='value(httpRequest.status)' 2>/dev/null || true)"

  # Próximo intento programado por el Scheduler
  NEXT_TS="$(gcloud scheduler jobs describe "${JOB_ID}" \
    --location="${LOCATION}" --project="${PROJECT}" \
    --format='value(scheduleTime)' 2>/dev/null || true)"

  if [ -n "${LAST_TS:-}" ] || [ -n "${LAST_CODE:-}" ]; then
    echo "- Último intento: ${LAST_TS:-_Sin datos_}"
    if [ -n "${LAST_CODE:-}" ]; then
      echo "- Resultado: HTTP ${LAST_CODE}"
    else
      echo "- Resultado: _Sin datos_"
    fi
  else
    echo "_Sin datos_"
  fi

  if [ -n "${NEXT_TS:-}" ]; then
  echo "- Próximo intento: ${NEXT_TS}"
else
  CRON="$(gcloud scheduler jobs describe "${JOB_ID}" --location="${LOCATION}" --project="${PROJECT}" --format='value(schedule)')" || true
  TZID="$(gcloud scheduler jobs describe "${JOB_ID}" --location="${LOCATION}" --project="${PROJECT}" --format='value(timeZone)')" || true
  echo "- Próximo intento: _Sin datos_ (cron: ${CRON:-n/a}, tz: ${TZID:-n/a})"
fi
} >> "$OUT_MD"

# ===== Scheduler history (last 3 /auto_heal requests) =====
{
  echo
  echo "### Scheduler history (run-auto-heal, last 3)"
  gcloud logging read \
    'resource.type="cloud_run_revision" AND resource.labels.service_name="natacha-health-monitor" AND httpRequest.requestUrl:"/auto_heal"' \
    --project="${PROJECT}" --limit=3 --order=desc \
    --format='table(timestamp:label=TIME, httpRequest.status:label=HTTP, httpRequest.requestMethod:label=METHOD)' \
    2>/dev/null || true
} >> "$OUT_MD"
