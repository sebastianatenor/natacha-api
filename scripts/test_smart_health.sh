#!/usr/bin/env bash
set -euo pipefail
URL="https://natacha-api-422255208682.us-central1.run.app/ops/smart_health"
resp=$(curl -sS "$URL" || true)
ok=$(echo "$resp" | jq -r '.ok' 2>/dev/null || echo "null")
if [ "$ok" = "true" ]; then
  echo "✅ smart_health OK → $resp"
  exit 0
else
  echo "❌ smart_health FAIL → $resp"
  exit 1
fi
