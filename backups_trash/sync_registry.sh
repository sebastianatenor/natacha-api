#!/usr/bin/env bash
set -euo pipefail

echo "══════════ Natacha Registry Sync — Inicio ══════════"

ROOT_REG="REGISTRY.md"
MIRROR_REG="knowledge/registry/REGISTRY.md"

# 1) Intento de sync con registry_check.py (si existe)
if [ -f scripts/registry_check.py ]; then
  echo "→ Usando scripts/registry_check.py (--sync-mirror | --sync)"
  python3 scripts/registry_check.py --sync-mirror 2>/dev/null || \
  python3 scripts/registry_check.py --sync 2>/dev/null || \
  true
else
  echo "→ Fallback: mantener espejo entre $ROOT_REG y $MIRROR_REG si ambos existen"
  mkdir -p "$(dirname "$MIRROR_REG")"
  if [ -f "$ROOT_REG" ]; then
    cp "$ROOT_REG" "$MIRROR_REG"
  elif [ -f "$MIRROR_REG" ]; then
    cp "$MIRROR_REG" "$ROOT_REG"
  else
    echo "⚠️  No hay REGISTRY.md ni knowledge/registry/REGISTRY.md; nada para sincronizar."
  fi
fi

# 2) Normalizar fin de línea y trailing spaces
if command -v dos2unix >/dev/null 2>&1; then
  dos2unix -q "$ROOT_REG" "$MIRROR_REG" 2>/dev/null || true
fi
if command -v sed >/dev/null 2>&1; then
  sed -i '' -e 's/[[:space:]]\+$//' "$ROOT_REG" 2>/dev/null || true
  sed -i '' -e 's/[[:space:]]\+$//' "$MIRROR_REG" 2>/dev/null || true
fi

# 3) Stage + commit (solo si hay cambios)
git add "$ROOT_REG" "$MIRROR_REG" 2>/dev/null || true

if ! git diff --cached --quiet; then
  TS="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
  git commit -m "sync(registry): capabilities update ($TS)"
  echo "✅ Registry sincronizado y commiteado."
else
  echo "ℹ️  No hay cambios para commitear."
fi

echo "══════════ Natacha Registry Sync — Fin ═════════════"
