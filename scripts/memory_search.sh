. "$(dirname "$0")/../tools/canon_resolver.sh" || source tools/canon_resolver.sh
resolve_canon # exporta CANONICAL
#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 1 ]; then
  echo "Uso: $0 \"termino a buscar\"" >&2
  exit 2
fi
TERM="$*"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "🔎 Buscando: \"$TERM\""
echo "— En árbol de código (tracked y untracked)…"
if command -v rg >/dev/null 2>&1; then
  rg -n --hidden --glob '!.git' "$TERM" || true
else
  grep -Rni --exclude-dir='.git' "$TERM" . || true
fi

echo
echo "— En memoria (knowledge/)…"
if command -v rg >/dev/null 2>&1; then
  rg -n --hidden --glob 'knowledge/**' "$TERM" || true
else
  grep -Rni --exclude-dir='.git' "$TERM" knowledge/ || true
fi

echo
echo "— Coincidencias de archivo exacto…"
git ls-files | awk -v t="$TERM" 'tolower($0)==tolower(t){print "  ",$0}'
