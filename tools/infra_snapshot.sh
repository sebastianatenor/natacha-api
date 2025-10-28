#!/usr/bin/env bash
set -Eeuo pipefail

log() { printf '%s %s\n' "$(date -u +%H:%M:%SZ)" "$*"; }
run() {
  local fname="$1"; shift
  log "▶ ${fname}"
  { "$@" >"${OUT}/${fname}.out" 2>"${OUT}/${fname}.err"; } || true
  log "✓ ${fname}"
}

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${ROOT}/infra_snapshots"
mkdir -p "${OUT_DIR}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="${OUT_DIR}/${STAMP}"
mkdir -p "${OUT}"

log "Snapshot Natacha — inicio"
log "ROOT=${ROOT}"
log "OUT=${OUT}"

PROJECT="${PROJECT:-asistente-sebastian}"
REGION="${GCP_REGION:-us-central1}"

# ---- Sistema / herramientas
run sys.uname uname -a
# macOS details (best effort)
if command -v sw_vers >/dev/null 2>&1; then run sys.macos sw_vers; fi
run sys.shell echo "$SHELL"
run sys.python python3 -c 'import sys,platform;print(sys.executable, platform.python_version())' || true
run sys.python_version python3 -V || true
run sys.pip_show python3 -m pip show google-auth google-cloud-firestore fastapi uvicorn || true
run sys.gcloud gcloud --version || true
run sys.docker docker --version || true

# ---- Git
cd "${ROOT}"
run git.root git rev-parse --show-toplevel
run git.status git status --porcelain=v1
run git.remote git remote -v
run git.last git --no-pager log --oneline --decorate --graph -15

# ---- Cloud Run / Scheduler / Logging / Monitoring / Secrets / Firestore / PubSub / Cloud Build
run run.services gcloud run services list --platform=managed --region="${REGION}" --format=json
run sched.jobs gcloud scheduler jobs list --location="${REGION}" --format=json || true
run log.metrics gcloud logging metrics list --format=json || true
run mon.policies gcloud alpha monitoring policies list --format=json || true
run mon.channels gcloud alpha monitoring channels list --format=json || true
run mon.uptime gcloud monitoring uptime list-configs --format=json || true
run secrets gcloud secrets list --format=json || true
run firestore.info gcloud firestore databases describe --format=json || true
run firestore.indexes gcloud firestore indexes composite list || true
run pubsub.topics gcloud pubsub topics list --format=json || true
run pubsub.subs gcloud pubsub subscriptions list --format=json || true
run cloudbuild.triggers gcloud beta builds triggers list --format=json || true

# IAM focos
run iam.run_invokers gcloud projects get-iam-policy "${PROJECT}" --flatten="bindings[].members" --filter='bindings.role:roles/run.invoker' --format='table(bindings.role,bindings.members)' || true
run iam.run_viewers  gcloud projects get-iam-policy "${PROJECT}" --flatten="bindings[].members" --filter='bindings.role:roles/run.viewer'  --format='table(bindings.role,bindings.members)' || true

# ---- Últimos logs (-1h)
run log.sample gcloud logging read 'timestamp>="-1h"' --limit=50 --format='value(timestamp,resource.type,resource.labels.service_name,severity,textPayload)' || true

# ---- Best effort: /health y /auto_heal
SVC_URL="$(gcloud run services describe natacha-health-monitor --region="${REGION}" --format='value(status.url)' 2>/dev/null || true)"
if [ -n "${SVC_URL}" ]; then
  run http.health curl -sS -m 10 "${SVC_URL}/health"
  run http.auto_heal curl -sS -m 10 -X POST "${SVC_URL}/auto_heal"
fi

# ---- Tarball
tar -C "${OUT}/.." -czf "${OUT}.tar.gz" "$(basename "${OUT}")" || true
log "Snapshot listo: ${OUT}"
log "Tarball: ${OUT}.tar.gz"
