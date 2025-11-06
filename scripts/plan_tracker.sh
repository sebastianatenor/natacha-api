#!/usr/bin/env bash
# === Natacha PLAN TRACKER ===
# Registra avances y chequea progreso del plan técnico.

set -e
PLAN_FILE="logs/plan_status.log"
DATE="$(date '+%Y-%m-%d %H:%M:%S')"

log(){ echo "[$DATE] $*" | tee -a "$PLAN_FILE"; }

case "$1" in
  init)
    mkdir -p logs
    echo "== PLAN TRACKER INIT ==" > "$PLAN_FILE"
    log "✅ Iniciado plan de reconstrucción de infraestructura"
    ;;
  step)
    shift
    log "🔹 Paso: $*"
    ;;
  check)
    echo
    echo "📜 Historial de avances registrados:"
    cat "$PLAN_FILE"
    ;;
  mark)
    shift
    log "✅ Completado: $*"
    ;;
  *)
    echo "Uso: bash scripts/plan_tracker.sh [init|step|mark|check] 'texto descriptivo'"
    ;;
esac
