#!/usr/bin/env bash
set -euo pipefail

have(){ command -v "$1" >/dev/null 2>&1; }

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

PROJECT="$(gcloud config get-value project 2>/dev/null || echo '-')"
REGION_DEFAULT="${REGION_DEFAULT:-us-central1}"
REG_FILE="knowledge/registry/REGISTRY.md"

hr(){ printf '%*s\n' 60 | tr ' ' '─'; }

section(){
  echo
  hr
  echo "🔹 $1"
  hr
}

echo "══════════ Natacha Capabilities (snapshot local + GCP) ══════════"
echo "📦 Repo:       $(basename "$ROOT")"
echo "🧭 Proyecto:   ${PROJECT}"
echo "🌍 Región:     ${REGION_DEFAULT}"

# ─────────────────────────────────────────────────────────────
# 1) Registro (si existe)
# ─────────────────────────────────────────────────────────────
section "Registry"
if [ -f "$REG_FILE" ]; then
  awk 'NR<=10{print} NR==11{print "... (ver knowledge/registry/REGISTRY.md)"; exit}' "$REG_FILE"
else
  echo "No existe knowledge/registry/REGISTRY.md (aún)."
fi

# ─────────────────────────────────────────────────────────────
# 2) Uptime Check
# ─────────────────────────────────────────────────────────────
section "Monitoring • Uptime Check"
if have gcloud; then
  CHECK="$(gcloud monitoring uptime list-configs --format='value(name)' 2>/dev/null | head -n1 || true)"
  if [ -n "$CHECK" ]; then
    gcloud monitoring uptime describe "$CHECK" \
      --format='yaml(name,displayName,monitoredResource.labels.host,httpCheck.path,httpCheck.port,httpCheck.useSsl,period,timeout,selectedRegions)' || true
  else
    echo "No se detectó ningún uptime check."
  fi
else
  echo "gcloud no disponible."
fi

# ─────────────────────────────────────────────────────────────
# 3) Alert Policies (solo las de Uptime)
# ─────────────────────────────────────────────────────────────
section "Monitoring • Alert Policies (Uptime)"
if have gcloud; then
  gcloud alpha monitoring policies list \
    --filter='displayName:"CRun | HealthMonitor | Uptime"' \
    --format='table(name,displayName,enabled)' 2>/dev/null || true

  # Mostrar el detalle mínimo de cada una
  for P in $(gcloud alpha monitoring policies list \
      --filter='displayName:"CRun | HealthMonitor | Uptime"' \
      --format='value(name)' 2>/dev/null); do
    echo
    echo "• $P"
    gcloud alpha monitoring policies describe "$P" --format=json \
    | jq '{displayName,enabled,channel:(.notificationChannels[0] // "-"),
           filter:(.conditions[0].conditionThreshold.filter // "-"),
           duration:(.conditions[0].conditionThreshold.duration // "-"),
           aggregations:(.conditions[0].conditionThreshold.aggregations // [])}' 2>/dev/null || true
  done
else
  echo "gcloud no disponible."
fi

# ─────────────────────────────────────────────────────────────
# 4) Canales de notificación (email)
# ─────────────────────────────────────────────────────────────
section "Monitoring • Canales de Notificación"
if have gcloud; then
  gcloud alpha monitoring channels list \
    --format='table(name,displayName,type,labels.email_address)' 2>/dev/null || true
fi

# ─────────────────────────────────────────────────────────────
# 5) Cloud Run (servicios clave)
# ─────────────────────────────────────────────────────────────
section "Cloud Run • Servicios"
if have gcloud; then
  for SVC in natacha-health-monitor natacha-api natacha-whatsapp natacha-memory-console; do
    gcloud run services describe "$SVC" --region "$REGION_DEFAULT" \
      --format='value(metadata.name,status.url,status.latestReadyRevisionName)' 2>/dev/null \
    | awk 'NF {printf "• %-28s  URL: %-70s  Rev: %s\n",$1,$2,$3}'
  done
fi

# ─────────────────────────────────────────────────────────────
# 6) Dashboards locales (Streamlit/py)
# ─────────────────────────────────────────────────────────────
section "Dashboards locales (archivos *.py)"
git ls-files | grep -E '(^dashboard\.py$|^dashboard/.*\.py$)' || echo "— (no hay archivos de dashboard detectados) —"

# ─────────────────────────────────────────────────────────────
# 7) Scripts de operación (este y los de “cerebro”)
# ─────────────────────────────────────────────────────────────
section "Scripts de operación"
ls -1 scripts 2>/dev/null | sort || echo "— (no hay scripts) —"

echo
hr
echo "TIP: ejecutá  scripts/brain_sync.sh  para actualizar REGISTRY.md"
hr
