#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE:-${NATACHA_BASE_URL:-}}"
if [[ -z "${BASE}" ]]; then
  echo "❌ BASE vacío. Exportá BASE o configurá vars/secrets NATACHA_BASE_URL"; exit 1
fi

echo "🔎 Contract check contra $BASE"
OPENAPI="$(curl -sSf "$BASE/openapi.json")"

req_paths=(
  "/memory/v2/store"
  "/memory/v2/search"
  "/v1/tasks/search"
  "/v1/tasks/add"
)
opt_paths=(
  "/memory/search_safe"
)

fail=0
for p in "${req_paths[@]}"; do
  if jq -e --arg p "$p" '.paths | has($p)' <<<"$OPENAPI" >/dev/null; then
    echo "🟢 REQUIRED OK $p"
  else
    echo "🔴 REQUIRED MISSING $p"
    fail=1
  fi
done

for p in "${opt_paths[@]}"; do
  if jq -e --arg p "$p" '.paths | has($p)' <<<"$OPENAPI" >/dev/null; then
    echo "🟢 OPTIONAL PRESENT $p"
  else
    echo "🟡 OPTIONAL ABSENT $p (no bloquea)"
  fi
done

if [[ "$fail" -eq 0 ]]; then
  echo "✅ Contract: PASS"
else
  echo "❌ Contract: FAIL"; exit 1
fi
