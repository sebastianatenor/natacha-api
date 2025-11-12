#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE:-http://localhost:8080}"
ts=$(date +%Y%m%d-%H%M%S)

mkdir -p docs

curl -fsS "$BASE/openapi.json" -o "docs/openapi.$ts.json"
jq -r '.paths | keys[]' "docs/openapi.$ts.json" | sort > "docs/routes.$ts.txt"

echo "== Summary =="
echo "Total routes: $(wc -l < docs/routes.$ts.txt)"
echo "--- first 10 ---"
head -n 10 docs/routes.$ts.txt || true
echo "---------------"

# Si hay /ops, mostrarlos
ops_count=$(grep -c '/ops' docs/routes.$ts.txt || true)
if [ "$ops_count" -gt 0 ]; then
  echo "Ops routes ($ops_count):"
  grep '/ops' docs/routes.$ts.txt
else
  echo "No /ops routes detected (solo info)."
fi

echo "Artifacts:"
echo " - docs/openapi.$ts.json"
echo " - docs/routes.$ts.txt"
