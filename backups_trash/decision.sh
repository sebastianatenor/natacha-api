#!/usr/bin/env bash
set -euo pipefail
MSG="${*:-}"
[ -z "$MSG" ] && { echo "Uso: $0 \"Decisión…\""; exit 2; }
FILE="knowledge/cortex/DECISIONS.md"
TS="$(date +'%Y-%m-%d %H:%M')"
mkdir -p knowledge/cortex
touch "$FILE"
echo "- [$TS] $MSG" >> "$FILE"
echo "📝 Añadido a $FILE"
