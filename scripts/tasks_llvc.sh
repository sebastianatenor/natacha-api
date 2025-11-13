#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${BASE:-}" ]]; then
  echo "BASE no definido (ej: export BASE=...)" >&2
  exit 1
fi

if [[ -z "${KEY:-}" ]]; then
  echo "KEY no definido (usa gcloud ... o export KEY=...)" >&2
  exit 1
fi

PROJECT="${1:-LLVC}"
STATE="${2:-}"     # opcional: pending, done, vigente, etc.
LIMIT="${3:-10}"

# armamos los args SIN state (lo filtramos del lado del cliente)
curl_args=(
  -s -G "$BASE/tasks/list"
  -H "X-API-Key: $KEY"
  --data-urlencode "project=${PROJECT}"
  --data-urlencode "limit=${LIMIT}"
)

RESP="$(curl "${curl_args[@]}")"

echo "$RESP" \
  | jq --arg state "$STATE" '
      .items = (.items // []) |
      if $state == "" then
        .items[]
      else
        .items[] | select(.state == $state)
      end
      | {id,title,state,due,channel,project}
    '
