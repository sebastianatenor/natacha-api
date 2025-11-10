#!/usr/bin/env bash
set -euo pipefail
REGION="${REGION:-us-central1}"
services=(natacha-api natacha-api-stg natacha-api-stable natacha-dashboard natacha-memory-console)
for s in "${services[@]}"; do
  url=$(gcloud run services describe "$s" --region "$REGION" --format='value(status.url)' 2>/dev/null || true)
  [[ -z "$url" ]] && { echo "$s -> (sin URL)"; continue; }
  for path in /health /healthz /ops/ping /; do
    resp=$(curl -s -m 5 "$url$path" || true)
    code=$(curl -s -o /dev/null -w "%{http_code}" -m 5 "$url$path" || true)
    if [[ "$code" == "200" ]]; then
      if echo "$resp" | jq -e '.status=="ok"' >/dev/null 2>&1; then
        printf "%-22s -> JSON ok\n" "$s$path"
      else
        printf "%-22s -> 200 ok (no-JSON)\n" "$s$path"
      fi
      break
    fi
  done
done
