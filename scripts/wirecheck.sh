#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE:-${NATACHA_BASE_URL:-}}"
if [[ -z "${BASE}" ]]; then
  echo "❌ BASE vacío. Exportá BASE o configurá vars/secrets NATACHA_BASE_URL"; exit 1
fi

echo "🔎 Wirecheck contra $BASE"
OPENAPI="$(curl -sSf "$BASE/openapi.json")"

paths_sorted=$(jq -r '.paths | keys[]' <<<"$OPENAPI" | sort)
dups=$(echo "$paths_sorted" | uniq -d || true)
if [[ -n "$dups" ]]; then
  echo "🔴 Rutas duplicadas:"
  echo "$dups"
  exit 1
fi
echo "🟢 Sin rutas duplicadas"

must_have_any=(
  "^/memory/"
  "^/v1/tasks/"
  "^/ops/"
)
for re in "${must_have_any[@]}"; do
  if jq -e --arg re "$re" '(.paths | keys | map(test($re)) | any(.))' <<<"$OPENAPI" >/dev/null; then
    echo "🟢 Grupo OK $re"
  else
    echo "🔴 Falta algún path que matchee $re"
    exit 1
  fi
done

echo "✅ Wirecheck: PASS"
