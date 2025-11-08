CANONICAL="${NATACHA_CONTEXT_API:-https://natacha-api-mkwskljrhq-uc.a.run.app}"
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
REG="knowledge/registry/REGISTRY.md"
TMP_NEW="$(mktemp)"; TMP_OLD="$(mktemp)"; DIFF="/tmp/strict_diff.txt"

echo "══════════ Natacha Strict Mode — Verificación de cambios ══════════"
scripts/brain_sync.sh || true

grep -v '^_Última actualización' "$REG" > "$TMP_NEW" || true
if git show HEAD:"$REG" >/dev/null 2>&1; then
  git show HEAD:"$REG" 2>/dev/null | grep -v '^_Última actualización' > "$TMP_OLD" || true
else
  : > "$TMP_OLD"
fi

# diff: si hay diferencias, genera código de salida 1
if diff -u "$TMP_OLD" "$TMP_NEW" > "$DIFF"; then
  echo "✅ Sin diferencias de capacidad detectadas."
  : > "$DIFF"
else
  echo "⚠️  Cambios de capacidad detectados. Diff:"
  echo "────────────────────────────────────────────────────────────"
  sed 's/^/    /' "$DIFF" | sed -e '1,2d' || true
  echo "────────────────────────────────────────────────────────────"
  echo "💡 Acción: git add knowledge/registry/REGISTRY.md (o reintentar el commit)."
  exit 1
fi
echo "🧾 Registro: $REG"
echo "🧩 Diff temporal: $DIFF"
