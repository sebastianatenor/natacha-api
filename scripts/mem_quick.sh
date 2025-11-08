#!/usr/bin/env bash
# scripts/mem_quick.sh
# Helpers rápidos para Memory v2 (Natacha API)
# Requisitos: bash, curl, jq, gcloud autenticado en proyecto "asistente-sebastian"

set -euo pipefail

## =========[ Config ]=========
: "${PROJ:=asistente-sebastian}"
: "${REG:=us-central1}"
: "${SVC:=natacha-api}"
: "${NAMESPACE_DEFAULT:=user:sebastian}"
: "${JOB_COMPACT:=memv2-compact-nightly}"

## =========[ Preflight ]=========
need() { command -v "$1" >/dev/null 2>&1 || { echo "❌ Falta comando: $1"; exit 1; }; }
need curl; need jq; need gcloud

# Key
if [[ -z "${KEY:-}" ]]; then
  KEY="$(gcloud secrets versions access latest --secret NATACHA_API_KEY --project "$PROJ" | tr -d '\r\n')"
fi

# URL base (canónica 422…)
if [[ -z "${BASE:-}" ]]; then
  BASE="$(gcloud run services describe "$SVC" --project "$PROJ" --region "$REG" --format='value(status.url)' | tr -d '\r\n')"
fi

# Ping health
echo "== Sanity check =="
echo "KEY: ${#KEY} chars | BASE: $BASE"
curl -fsS -H "X-API-Key: $KEY" "$BASE/health" >/dev/null && echo "🟢 /health OK" || { echo "❌ /health FAIL"; exit 1; }

echo "== Rutas /memory* disponibles =="
curl -fsS -H "X-API-Key: $KEY" "$BASE/__debug_routes" \
| jq -r '.routes[] | select(.path|startswith("/memory")) | .path'

## =========[ Core helpers ]=========
mem_store () {
  local payload="${1:?JSON requerido}"
  curl -fsS -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
    -X POST "$BASE/memory/v2/store" -d "$payload" | jq .
}

mem_search () {
  local payload="${1:?JSON requerido}"
  curl -fsS -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
    -X POST "$BASE/memory/v2/search" -d "$payload" | jq .
}

mem_compact () {
  local payload="${1:?JSON requerido}"
  curl -fsS -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
    -X POST "$BASE/memory/v2/compact" -d "$payload" | jq .
}

mem_info () {
  curl -fsS -H "X-API-Key: $KEY" "$BASE/memory/v2/ops/memory-info" | jq .
}

## =========[ Shortcuts comunes ]=========
# 1) Buscar tareas de deck (limpia probes/internal)
mem_search_deck () {
  mem_search "{
    \"namespace\":\"${NAMESPACE_DEFAULT}\",
    \"query\":\"deck\",
    \"filters\":{\"type\":\"task\",\"tags_any\":[\"deck\",\"clientes\"],\"tags_none\":[\"probe\",\"internal\"]},
    \"limit\":10
  }"
}

# 2) Hechos de negocio LLVC (limpio)
mem_search_llvc () {
  mem_search "{
    \"namespace\":\"${NAMESPACE_DEFAULT}\",
    \"query\":\"LLVC\",
    \"filters\":{\"type\":\"fact\",\"tags_none\":[\"probe\",\"internal\"]},
    \"limit\":10
  }"
}

# 3) Decisiones de infra memv2
mem_search_memv2_decisions () {
  mem_search "{
    \"namespace\":\"${NAMESPACE_DEFAULT}\",
    \"query\":\"memv2\",
    \"filters\":{\"type\":\"decision\"},
    \"limit\":5
  }"
}

# 4) Compact real (sin dry-run)
mem_compact_now () {
  mem_compact "{
    \"namespace\":\"${NAMESPACE_DEFAULT}\",
    \"dry_run\": false
  }"
}

## =========[ Scheduler & Logs ]=========
# Ejecutar ahora el job de compact (vía Scheduler)
scheduler_run_compact () {
  gcloud scheduler jobs run "$JOB_COMPACT" --location="$REG"
}

# Ver últimos logs del endpoint /memory/v2/compact en Cloud Run
logs_compact_recent () {
  gcloud logging read \
    'resource.type="cloud_run_revision" AND httpRequest.requestUrl:"/memory/v2/compact"' \
    --limit=20 --format="value(textPayload)"
}

# Ver último resultado del Scheduler
logs_scheduler_recent () {
  gcloud logging read \
    "resource.type=cloud_scheduler_job AND resource.labels.job_id=\"$JOB_COMPACT\"" \
    --limit=10 --format="value(textPayload,timestamp)"
}

## =========[ Plantillas de guardado ]=========
mem_store_decision_compact_cron () {
  mem_store "{
    \"namespace\": \"${NAMESPACE_DEFAULT}\",
    \"items\": [{
      \"type\":\"decision\",
      \"text\":\"Memv2 compact nightly a las 03:00 ART vía Cloud Scheduler.\",
      \"source\":\"ops\",
      \"tags\":[\"infra\",\"memv2\",\"scheduler\"],
      \"meta\":{\"job\":\"${JOB_COMPACT}\",\"cron\":\"0 6 * * *\",\"tz\":\"UTC=>03ART\"}
    }]
  }"
}

mem_store_fact_llvc_deck () {
  mem_store "{
    \"namespace\": \"${NAMESPACE_DEFAULT}\",
    \"items\": [{
      \"type\":\"fact\",
      \"text\":\"Contacto Nubicom y Aguas del Norte esperan deck de importación usada.\",
      \"source\":\"chatgpt\",
      \"tags\":[\"llvc\",\"clientes\",\"deck\"]
    }]
  }"
}

mem_store_task_deck_envio () {
  mem_store "{
    \"namespace\": \"${NAMESPACE_DEFAULT}\",
    \"items\": [{
      \"type\":\"task\",
      \"text\":\"Enviar deck actualizado a Nubicom y Aguas del Norte.\",
      \"source\":\"chatgpt\",
      \"tags\":[\"ventas\",\"deck\",\"clientes\"],
      \"meta\":{\"deadline\":\"2025-11-15\",\"owner\":\"Sebastián\"}
    }]
  }"
}

## =========[ Namespace ops para probes ]=========
mem_store_probe_ops () {
  mem_store "{
    \"namespace\":\"ops:probes\",
    \"items\":[{\"type\":\"fact\",\"text\":\"Write-to-GCS control\",\"source\":\"probe\",\"tags\":[\"probe\",\"gcs\",\"internal\"]}]
  }"
}

# =======[ Sugar: store rápido ]=======
mem_store_quick() {
  local ns="${1:-$NAMESPACE_DEFAULT}"
  local type="${2:-fact}"
  shift 2 || true
  local text="$*"
  [[ -z "$text" ]] && { echo "Uso: mem_store_quick [namespace] [type] <texto>"; return 1; }
  curl -fsS -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
    -X POST "$BASE/memory/v2/store" -d "{
      \"namespace\":\"$ns\",
      \"items\":[{\"type\":\"$type\",\"text\":\"$text\",\"source\":\"chatgpt\"}]
    }" | jq .
}

mem_store_task_quick() {
  local ns="${1:-$NAMESPACE_DEFAULT}"
  local deadline="${2:-}"
  shift 2 || true
  local text="$*"
  [[ -z "$text" ]] && { echo "Uso: mem_store_task_quick [namespace] [deadline:YYYY-MM-DD] <texto>"; return 1; }
  curl -fsS -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
    -X POST "$BASE/memory/v2/store" -d "{
      \"namespace\":\"$ns\",
      \"items\":[{\"type\":\"task\",\"text\":\"$text\",\"source\":\"chatgpt\",\"tags\":[\"task\"],\"meta\":{\"deadline\":\"$deadline\",\"owner\":\"Sebastián\"}}]
    }" | jq .
}

## =========[ Ayuda ]=========
usage () {
  cat <<'USAGE'
Comandos útiles:
  ./scripts/mem_quick.sh mem_info
  ./scripts/mem_quick.sh mem_search_deck
  ./scripts/mem_quick.sh mem_search_llvc
  ./scripts/mem_quick.sh mem_search_memv2_decisions
  ./scripts/mem_quick.sh mem_compact_now
  ./scripts/mem_quick.sh scheduler_run_compact
  ./scripts/mem_quick.sh logs_compact_recent
  ./scripts/mem_quick.sh logs_scheduler_recent

Atajos rápidos:
  ./scripts/mem_quick.sh mem_store_quick [ns] [type] <texto>
  ./scripts/mem_quick.sh mem_store_task_quick [ns] [YYYY-MM-DD] <texto>

Plantillas:
  ./scripts/mem_quick.sh mem_store_decision_compact_cron
  ./scripts/mem_quick.sh mem_store_fact_llvc_deck
  ./scripts/mem_quick.sh mem_store_task_deck_envio
  ./scripts/mem_quick.sh mem_store_probe_ops
USAGE
}

## =========[ Dispatcher ]=========
cmd="${1:-usage}"
shift || true
case "$cmd" in
  mem_store|mem_search|mem_compact|mem_info|\
  mem_search_deck|mem_search_llvc|mem_search_memv2_decisions|\
  mem_compact_now|scheduler_run_compact|logs_compact_recent|logs_scheduler_recent|\
  mem_store_decision_compact_cron|mem_store_fact_llvc_deck|mem_store_task_deck_envio|mem_store_probe_ops|\
  mem_store_quick|mem_store_task_quick|usage)
    "$cmd" "$@"
    ;;
  *)
    echo "Comando desconocido: $cmd"
    usage
    exit 1
    ;;
esac
