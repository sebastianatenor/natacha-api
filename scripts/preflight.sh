#!/usr/bin/env bash
# shellcheck shell=bash
. "$(dirname "$0")/../tools/canon_resolver.sh" || source tools/canon_resolver.sh
resolve_canon # exporta CANONICAL
#!/usr/bin/env bash
set -euo pipefail

# Uso:
#   scripts/preflight.sh --intent "crear-alert-policy" --name "CRun | HealthMonitor | Uptime / down"
#   scripts/preflight.sh --intent "crear-dashboard" --file "dashboard.py"
#   scripts/preflight.sh --intent "crear-uptime" --host "natacha-health-monitor-422255208682.us-central1.run.app"

have() { command -v "$1" >/dev/null 2>&1; }
FIND(){ if have rg; then rg -n --hidden -S "$1" || true; else grep -Rni --exclude-dir=.git "$1" . || true; fi; }

INTENT="${1:-}"; shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --intent) shift; INTENT="${1:-}";;
    --name) shift; NAME="${1:-}";;
    --file) shift; FILE="${1:-}";;
    --host) shift; HOST="${1:-}";;
  esac
  shift || true
done

echo "▶ Preflight intent: ${INTENT:-<no-intent>}"

case "$INTENT" in
  crear-alert-policy)
    if [[ -z "${NAME:-}" ]]; then echo "Falta --name"; exit 2; fi
    echo "• Buscando policy displayName: $NAME"
    MATCHES=$(FIND "\"displayName\": \"$NAME\"" | wc -l | tr -d ' ')
    if [[ "$MATCHES" -gt 0 ]]; then
      echo "✖ Ya existe una policy con ese displayName en el repo:"
      FIND "\"displayName\": \"$NAME\""
      exit 3
    fi
    echo "• Verificando en GCP…"
    gcloud alpha monitoring policies list --format=json \
    | jq -r '.[]?.displayName' | grep -Fx "$NAME" >/dev/null && {
      echo "✖ Ya existe en GCP una policy con ese displayName"
      exit 4
    }
    echo "✔ OK: no hay duplicados."
    ;;

  crear-dashboard)
    if [[ -z "${FILE:-}" ]]; then echo "Falta --file"; exit 2; fi
    if [[ -f "$FILE" ]]; then
      echo "✖ Ya existe el archivo $FILE"
      exit 3
    fi
    echo "• Buscando dashboards similares…"
    FIND "streamlit" | head -n 10 || true
    echo "✔ OK: no existe $FILE"
    ;;

  crear-uptime)
    if [[ -z "${HOST:-}" ]]; then echo "Falta --host"; exit 2; fi
    echo "• Chequeando uptime para host: $HOST"
    gcloud monitoring uptime list-configs --format=json \
    | jq -r '.[]?.monitoredResource.labels.host // ""' \
    | grep -Fx "$HOST" >/dev/null && {
      echo "✖ Ya existe un uptime para $HOST"
      exit 3
    }
    echo "✔ OK: no existe uptime check duplicado."
    ;;

  *)
    echo "Intents soportados: crear-alert-policy | crear-dashboard | crear-uptime"
    exit 1
    ;;
esac
