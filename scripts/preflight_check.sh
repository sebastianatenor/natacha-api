#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 1 ]; then
  echo "Uso: $0 <ruta/archivo>" >&2
  exit 2
fi
TARGET="$1"
if [ -e "$TARGET" ]; then
  echo "⛔ Preflight: ya existe: $TARGET" >&2
  echo "Primeras líneas:" >&2
  head -n 20 "$TARGET" 2>/dev/null || true
  exit 3
fi
echo "✅ Preflight OK: no existe $TARGET"
