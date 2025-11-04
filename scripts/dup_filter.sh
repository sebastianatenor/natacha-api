#!/usr/bin/env bash
set -euo pipefail

PATTERN='(^|/)(\.venv|__pycache__|logs|backups)(/|$)|\.dist-info/|\.pyc$'
CORE='^(routes|scripts|knowledge|docs)(/|$)'
AUDIT='^knowledge/registry/audit(/|$)'

RAW="$(scripts/dup_scan.py 2>/dev/null || echo '{}')"

printf '%s\n' "$RAW" | jq --arg pat "$PATTERN" --arg core "$CORE" --arg audit "$AUDIT" '
  .findings = ((.findings // [])                                   # si es null → []
    | map(select( ( .a|test($pat)|not ) and ( .b|test($pat)|not ) ))
    | map(.strict = (
        (.a|test($core)) and (.b|test($core))                       # solo “core”
        and ((.a|test($audit)|not) and (.b|test($audit)|not))       # excluir audit
        and (.type=="near_duplicate_name") and (.similarity >= 0.94)
      ))
  )
  | .critical_count = ([ (.findings // [])[] | select(.strict==true) ] | length)
  | .has_criticals = (.critical_count > 0)
' || echo '{"findings":[],"critical_count":0,"has_criticals":false}'
