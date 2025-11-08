#!/usr/bin/env bash
set -euo pipefail
PATTERN='https://natacha-api-(422255208682\.us-central1|mkwskljrhq-uc\.a)\.run\.app'

# Lista de archivos trackeados y relevantes
mapfile -t FILES < <(
  git ls-files \
    | grep -E '^(routes|dashboard|scripts|legacy|system)/' \
    | grep -vE '(\.bak($|\.|/)|/\.backup_|^infra_snapshots/|^SNAPSHOTS/)'
)

# Si no hay archivos, salir limpio
[ ${#FILES[@]} -eq 0 ] && { echo "✅ Sin hardcodes"; exit 0; }

# Grep controlado
if grep -nE "$PATTERN" "${FILES[@]}"; then
  echo "❌ Hardcodes detectados" >&2
  exit 1
fi

echo "✅ Sin hardcodes"
