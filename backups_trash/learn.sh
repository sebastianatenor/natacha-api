#!/usr/bin/env bash
set -euo pipefail
TITLE="${1:-}"; shift || true
[ -z "$TITLE" ] && { echo "Uso: $0 \"Título\""; exit 2; }
BODY="${*:-}"
FN="knowledge/cortex/$(date +'%Y-%m-%d')_${TITLE// /_}.md"
cat > "$FN" <<MD
# $TITLE
**Fecha:** $(date +'%Y-%m-%d %H:%M')

$BODY
MD
echo "📚 Aprendizaje guardado en $FN"
