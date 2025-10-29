#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="knowledge/registry/audit"
mkdir -p "$OUT_DIR"

COMMIT_ID=$(git rev-parse --short HEAD 2>/dev/null || echo "uncommitted")
STAMP=$(date '+%Y%m%d-%H%M%S')
FILE="$OUT_DIR/audit_${STAMP}_${COMMIT_ID}.json"

# Recopilar info
{
  echo '{'
  echo "  \"timestamp\": \"$(date '+%Y-%m-%d %H:%M:%S %z')\","
  echo "  \"commit_id\": \"${COMMIT_ID}\","
  echo "  \"user\": \"${USER:-unknown}\","
  echo "  \"branch\": \"$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '-')\","
  echo '  "strict_check":'
  scripts/natacha_strict_check.sh || true
  echo ','
  echo '  "dup_scan":'
  scripts/dup_scan.py 2>/dev/null || echo '{}'
  echo '}'
} > "$FILE"

echo "🧾 Audit log generado: $FILE"
