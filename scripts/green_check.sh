#!/usr/bin/env bash
set -euo pipefail
CANON="$1"; SA="$2"
IDTOKEN="$(gcloud auth print-identity-token --impersonate-service-account="$SA" --audiences="$CANON")"
curl -fsS -H "Authorization: Bearer $IDTOKEN" "$CANON/ops/health" >/dev/null
curl -fsS -H "Authorization: Bearer $IDTOKEN" "$CANON/ops/version" >/dev/null
echo "✅ GREEN"
