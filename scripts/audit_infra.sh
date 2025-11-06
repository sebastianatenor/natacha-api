#!/usr/bin/env bash
set -euo pipefail

OUTDIR="${OUTDIR:-/tmp/natacha-audit-$(date +%Y%m%d-%H%M%S)}"
mkdir -p "$OUTDIR"

echo "Writing audit to $OUTDIR"

# Basic project info
PROJECT="$(gcloud config get-value project 2>/dev/null || echo '')"
PROJECT_NUM="$(gcloud projects describe "$PROJECT" --format='value(projectNumber)' 2>/dev/null || echo '')"
REGION="$(gcloud config get-value run/region 2>/dev/null || echo 'us-central1')"

echo "{ \"project\": \"$PROJECT\", \"project_number\": \"$PROJECT_NUM\", \"region\": \"$REGION\" }" > "$OUTDIR/summary.json"

# 1) Cloud Run services + full describe + revisions
echo "Listing Cloud Run services..."
gcloud run services list --region "$REGION" --format='json' > "$OUTDIR/run_services.json" || true

jq -r '.[].metadata.name' "$OUTDIR/run_services.json" | while read -r svc; do
  echo "Describing service $svc..."
  gcloud run services describe "$svc" --region "$REGION" --format='json' > "$OUTDIR/run_service_${svc}.json" || true
  # revisions (last 50)
  gcloud run revisions list --service "$svc" --region "$REGION" --limit=50 --format='json' > "$OUTDIR/run_revisions_${svc}.json" || true
  # extract container image and envs
  jq '{name: .metadata.name, url:.status.url, latestCreatedRevisionName:.status.latestCreatedRevisionName, traffic:.status.traffic, containers:.spec.template.spec.containers }' "$OUTDIR/run_service_${svc}.json" > "$OUTDIR/run_service_${svc}_summary.json" || true
done

# 2) Registry file if exists (REGISTRY.md)
if [ -f REGISTRY.md ]; then
  cp REGISTRY.md "$OUTDIR/REGISTRY.md"
elif [ -f ~/natacha-api/REGISTRY.md ]; then
  cp ~/natacha-api/REGISTRY.md "$OUTDIR/REGISTRY.md"
fi

# 3) Env vars (for each service) - already in run_service_<svc>.json; create a consolidated summary
jq -s 'map(.containers[0].env // []) | add' "$OUTDIR/run_services.json" > "$OUTDIR/run_envs_concat.json" 2>/dev/null || true

# 4) IAM: service accounts and who can invoke Cloud Run
gcloud iam service-accounts list --format='json' > "$OUTDIR/service_accounts.json" || true
# For each Cloud Run service check policy
jq -r '.[].metadata.name' "$OUTDIR/run_services.json" | while read -r svc; do
  echo "Fetching IAM policy for $svc..."
  gcloud run services get-iam-policy "$svc" --region "$REGION" --format='json' > "$OUTDIR/run_${svc}_iam.json" || true
done

# 5) Secrets
gcloud secrets list --format='json' > "$OUTDIR/secrets.json" || true

# 6) GCS buckets (list) and check for Firestore export target
gsutil ls > "$OUTDIR/gcs_buckets_ls.txt" 2>/dev/null || true
gcloud storage buckets list --format='json' > "$OUTDIR/gcs_buckets.json" 2>/dev/null || true

# 7) Firestore: list collections is not native in gcloud, but we can request an export (opt-in)
# Create a temporary export bucket if needed (does not create if exists)
EXPORT_BUCKET="${EXPORT_BUCKET:-natacha-firestore-backups-$PROJECT_NUM}"
if ! gsutil ls -b "gs://$EXPORT_BUCKET" >/dev/null 2>&1; then
  echo "Creating backup bucket gs://$EXPORT_BUCKET (location same as project default)"
  gsutil mb -p "$PROJECT" -c STANDARD -l US-CENTRAL1 "gs://$EXPORT_BUCKET" 2>/dev/null || true
fi

# Export Firestore (may take seconds->minutes). If Firestore not enabled this will error but will be captured.
echo "Starting Firestore export to gs://$EXPORT_BUCKET/firestore-export-$(date +%Y%m%d-%H%M%S)/"
gcloud firestore export "gs://$EXPORT_BUCKET/firestore-export-$(date +%Y%m%d-%H%M%S)/" --project "$PROJECT" --format='json' > "$OUTDIR/firestore_export_cmd.json" 2>/dev/null || true

# 8) Cloud Build triggers and images
gcloud beta builds triggers list --format='json' > "$OUTDIR/cloudbuild_triggers.json" 2>/dev/null || true
gcloud container images list --repository="us-central1-docker.pkg.dev/$PROJECT" --format='json' > "$OUTDIR/container_images.json" 2>/dev/null || true

# 9) Recent logs for Cloud Run service revisions (last 100 lines)
jq -r '.[].metadata.name' "$OUTDIR/run_services.json" | while read -r svc; do
  REV="$(jq -r '.[] | select(.metadata.name=="'"$svc"'") | .status.latestCreatedRevisionName' "$OUTDIR/run_services.json" 2>/dev/null || true)"
  if [[ -n "$REV" && "$REV" != "null" ]]; then
    gcloud logging read \
      "resource.type=cloud_run_revision AND resource.labels.service_name=\"$svc\" AND resource.labels.revision_name=\"$REV\"" \
      --project "$PROJECT" --limit=200 --freshness=1h --format='json' > "$OUTDIR/logs_${svc}_rev_${REV}.json" || true
  fi
done

# 10) OpenAPI check: for every service canonical URL, verify servers[0].url equality if present
echo "Checking OpenAPI servers[0].url for each canonical..."
jq -r '.[].metadata.name' "$OUTDIR/run_services.json" | while read -r svc; do
  CANON="$(jq -r '.[] | select(.metadata.name=="'"$svc"'") | .spec.template.spec.containers[0].env[]? | select(.name=="OPENAPI_PUBLIC_URL") | .value' "$OUTDIR/run_services.json" 2>/dev/null || true)"
  # fallback to canonical format
  if [[ -z "$CANON" ]]; then
    CANON="https://${svc}-${PROJECT_NUM}.${REGION}.run.app"  # CANONICAL_OK
  fi
  # fetch server entry
  OPENAPI_SERVERS_URL="$(curl -s "${CANON}/openapi.v1.json" | jq -r '.servers[0].url // empty' || true)"
  printf '%s\n' "{\"service\":\"$svc\",\"canon\":\"$CANON\",\"openapi_servers0\":\"$OPENAPI_SERVERS_URL\"}" >> "$OUTDIR/openapi_checks.json"
done

# 11) Save current Makefile and scripts folder
if [ -f Makefile ]; then cp Makefile "$OUTDIR/Makefile" || true; fi
if [ -d scripts ]; then cp -r scripts "$OUTDIR/scripts" || true; fi

# 12) Small top-level human-readable summary
cat > "$OUTDIR/README.txt" <<EOF
Natacha audit report
Project: $PROJECT ($PROJECT_NUM)
Region: $REGION
Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

Files:
- run_services.json
- run_service_<svc>.json (per service)
- run_revisions_<svc>.json (per service)
- run_<svc>_iam.json (per service)
- secrets.json
- service_accounts.json
- gcs_buckets.json
- firestore_export_cmd.json (may be empty if export failed)
- openapi_checks.json (report of canonical vs servers[0].url)
- Makefile, scripts/ (copied if present)
- logs_*.json (recent logs)
- REGISTRY.md (if present)

Next suggested steps:
1) Inspect openapi_checks.json to ensure servers[0].url matches your canonical URL(s).
2) Review run_service_*_summary.json to see OPENAPI_PUBLIC_URL and envs.
3) Review run_<svc>_iam.json to ensure only expected members (service accounts, CI) have run.invoker.
4) Check secrets.json for secret names used in runtime.
5) Use the backup bucket gs://$EXPORT_BUCKET for Firestore recovery if needed.

EOF

echo "Audit done. Directory: $OUTDIR"
echo "Tip: tar -czf /tmp/natacha-audit.tgz -C $(dirname "$OUTDIR") $(basename "$OUTDIR")"
