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
LIMIT="${2:-50}"

RESP="$(curl -s -G "$BASE/tasks/list" \
  -H "X-API-Key: $KEY" \
  --data-urlencode "project=${PROJECT}" \
  --data-urlencode "limit=${LIMIT}")"

echo "$RESP" | jq '
  .items = (.items // []) 
  | .items |= map(
      . + {
        due_ts: (
          (.due // "") 
          | if . == "" then null 
            else (try (fromdateiso8601) catch null) 
            end
        )
      }
    )
  | . as $root
  | {
      summary: {
        total:        ($root.items | length),
        with_due:     ($root.items | map(select(.due_ts != null)) | length),
        without_due:  ($root.items | map(select(.due_ts == null)) | length),
        overdue:      ($root.items | map(select(.due_ts != null and .due_ts < now)) | length),
        due_next_7d:  ($root.items | map(select(.due_ts != null and .due_ts >= now and .due_ts < (now + 7*24*60*60))) | length)
      },
      upcoming: (
        $root.items
        | map(
            select(.due_ts != null and .due_ts >= now)
            | {id,title,state,due,channel,project,due_ts}
          )
        | sort_by(.due_ts)
        | .[:5]
      )
    }
'
