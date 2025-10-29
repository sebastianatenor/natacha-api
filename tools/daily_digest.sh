#!/bin/zsh
set -euo pipefail

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
