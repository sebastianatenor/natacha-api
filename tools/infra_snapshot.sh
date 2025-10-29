#!/bin/zsh
# === Natacha Infra Snapshot ===

set -euo pipefail

TS=$(date -u +"%Y%m%dT%H%M%SZ")
ROOT="$HOME/Projects/natacha-api"
OUT="$ROOT/infra_snapshots/$TS"
mkdir -p "$OUT"

log() { echo "$(date -u +"%H:%M:%SZ") $*"; }

log "Snapshot Natacha — inicio"
log "ROOT=$ROOT"
log "OUT=$OUT"

PROJECT="asistente-sebastian"
REGION="us-central1"
LOCATION="us-central1"

# ================== SISTEMA ==================
log "▶ sys.uname"
uname -a > "$OUT/sys.uname" && log "✓ sys.uname"

log "▶ sys.macos"
{ sw_vers; echo; sw_vers -productName 2>/dev/null || true; } > "$OUT/sys.macos" && log "✓ sys.macos"

log "▶ sys.shell"
echo $SHELL > "$OUT/sys.shell" && log "✓ sys.shell"

log "▶ sys.python"
command -v python3 > "$OUT/sys.python" && log "✓ sys.python"

log "▶ sys.python_version"
python3 --version > "$OUT/sys.python_version" && log "✓ sys.python_version"

log "▶ sys.pip_show"
pip show google-cloud-run google-cloud-scheduler > "$OUT/sys.pip_show" 2>/dev/null || true
log "✓ sys.pip_show"

log "▶ sys.gcloud"
gcloud version > "$OUT/sys.gcloud" && log "✓ sys.gcloud"

log "▶ sys.docker"
(docker --version || echo "Docker no instalado") > "$OUT/sys.docker"
log "✓ sys.docker"

# ================== GIT ==================
log "▶ git.root"
git rev-parse --show-toplevel > "$OUT/git.root" && log "✓ git.root"

log "▶ git.status"
git status > "$OUT/git.status" && log "✓ git.status"

log "▶ git.remote"
git remote -v > "$OUT/git.remote" && log "✓ git.remote"

log "▶ git.last"
git log -1 > "$OUT/git.last" && log "✓ git.last"

# ================== CLOUD RUN ==================
log "▶ run.services"
gcloud run services list \
  --platform managed \
  --region="$REGION" \
  --project="$PROJECT" \
  --format=json > "$OUT/run.services.json"
log "✓ run.services"

# ================== SCHEDULER ==================
log "▶ sched.jobs"
gcloud scheduler jobs list \
  --location="$LOCATION" \
  --project="$PROJECT" \
  --format=json > "$OUT/sched.jobs.json"
log "✓ sched.jobs"

# ================== LOGS ==================
log "▶ log.metrics"
gcloud logging metrics list \
  --project="$PROJECT" \
  --format=json > "$OUT/log.metrics.json"
log "✓ log.metrics"

# ================== MONITORING ==================
log "▶ mon.policies"
gcloud alpha monitoring policies list \
  --project="$PROJECT" \
  --format=json > "$OUT/mon.policies.json"
log "✓ mon.policies"

log "▶ mon.channels"
gcloud alpha monitoring channels list \
  --project="$PROJECT" \
  --format=json > "$OUT/mon.channels.json"
log "✓ mon.channels"

log "▶ mon.uptime"
gcloud monitoring uptime list-configs \
  --project="$PROJECT" \
  --format=json > "$OUT/mon.uptime.json"
log "✓ mon.uptime"

# ================== SECRETS ==================
log "▶ secrets"
gcloud secrets list \
  --project="$PROJECT" \
  --format=json > "$OUT/secrets.json"
log "✓ secrets"

# ================== FIRESTORE ==================
log "▶ firestore.info"
gcloud firestore databases describe \
  --project="$PROJECT" \
  --format=json > "$OUT/firestore.info.json" 2>/dev/null || echo "{}" > "$OUT/firestore.info.json"
log "✓ firestore.info"

log "▶ firestore.indexes"
gcloud firestore indexes composite list \
  --project="$PROJECT" \
  --format=json > "$OUT/firestore.indexes.json" 2>/dev/null || echo "[]" > "$OUT/firestore.indexes.json"
log "✓ firestore.indexes"

# ================== PUBSUB ==================
log "▶ pubsub.topics"
gcloud pubsub topics list \
  --project="$PROJECT" \
  --format=json > "$OUT/pubsub.topics.json"
log "✓ pubsub.topics"

log "▶ pubsub.subs"
gcloud pubsub subscriptions list \
  --project="$PROJECT" \
  --format=json > "$OUT/pubsub.subs.json"
log "✓ pubsub.subs"

# ================== CLOUDBUILD ==================
log "▶ cloudbuild.triggers"
gcloud builds triggers list \
  --project="$PROJECT" \
  --format=json > "$OUT/cloudbuild.triggers.json"
log "✓ cloudbuild.triggers"

# ================== IAM ==================
log "▶ iam.run_invokers"
gcloud projects get-iam-policy "$PROJECT" \
  --flatten="bindings[]" \
  --filter="bindings.role:roles/run.invoker" \
  --format=json > "$OUT/iam.run_invokers.json"
log "✓ iam.run_invokers"

log "▶ iam.run_viewers"
gcloud projects get-iam-policy "$PROJECT" \
  --flatten="bindings[]" \
  --filter="bindings.role:roles/run.viewer" \
  --format=json > "$OUT/iam.run_viewers.json"
log "✓ iam.run_viewers"

# ================== LOGS JSON ==================
log "Capturando logs de Cloud Run (última hora)"
gcloud logging read 'resource.type="cloud_run_revision" AND timestamp>="-1h"' \
  --limit=200 \
  --format=json \
  --project="$PROJECT" > "$OUT/log.sample.json" 2> "$OUT/log.sample.err" || true

# ================== HTTP CHECKS ==================
log "▶ http.health"
{ CODE=20 20 12 61 79 80 81 701 33 98 100 204 250 395 398 399 400curl -sS -o "/http.health.body" -w "%{http_code}" "https://natacha-api-mkwskljrhq-uc.a.run.app/"); echo "" > "/http.health.code"; } || echo "N/A" > "/http.health.code"
log "✓ http.health"

log "▶ http.auto_heal"
{ CODE=20 20 12 61 79 80 81 701 33 98 100 204 250 395 398 399 400curl -sS -X POST -o "/http.auto_heal.body" -w "%{http_code}" "https://natacha-health-monitor-mkwskljrhq-uc.a.run.app/auto_heal"); echo "" > "/http.auto_heal.code"; } || echo "N/A" > "/http.auto_heal.code"
log "✓ http.auto_heal"

# ================== COMPRESIÓN ==================
log "Snapshot listo: $OUT"
tar -czf "$OUT.tar.gz" -C "$OUT" . && log "Tarball: $OUT.tar.gz"
