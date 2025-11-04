#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-.}"
TS="$(date +%Y%m%d-%H%M%S)"
ARCHIVE="backup-suspects-${TS}.tar.gz"

# Carpetas a excluir (no tocamos venv, .git, etc.)
EXCLUDES=(
  -path "./.git" -prune -o
  -path "./venv" -prune -o
  -path "./.venv" -prune -o
  -path "./node_modules" -prune -o
  -path "./.terraform" -prune -o
  -path "./.idea" -prune -o
  -path "./__pycache__" -prune -o
  -path "./secrets" -prune -o
)

# Patrones sospechosos
PATTERNS=(
  -name "*.bak" -o
  -name "*.bak.*" -o
  -name "*~" -o
  -name "*.old" -o
  -name "*.orig" -o
  -name "*.rej" -o
  -name "*.swp" -o
  -name "*.swo" -o
  -name "*.log" -o
  -name ".DS_Store" -o
  -name "*.pyc" -o
  -path "*/__pycache__/*" -o
  -name "REGISTRY.backup.md"
)

DRYRUN="${DRYRUN:-1}"  # por defecto, solo muestra

echo "==> Buscando candidatos en: ${ROOT_DIR}"
# Build del comando find
# shellcheck disable=SC2068
CANDIDATES=$(eval find "${ROOT_DIR}" \( ${EXCLUDES[@]} -false -o -type f \( ${PATTERNS[@]} -false \) \) -print | sort)

if [[ -z "${CANDIDATES}" ]]; then
  echo "✔ No se encontraron archivos sospechosos."
  exit 0
fi

echo "==> Candidatos encontrados:"
echo "${CANDIDATES}" | sed 's/^/   - /'

# Respaldo en tar.gz
echo "==> Creando respaldo: ${ARCHIVE}"
# shellcheck disable=SC2001
echo "${CANDIDATES}" | tar -czf "${ARCHIVE}" -T - 2>/dev/null || true
echo "   Archivo de respaldo listo: ${ARCHIVE}"

if [[ "${DRYRUN}" == "1" ]]; then
  echo "🔎 DRY-RUN activado (no se borra nada)."
  echo "   Para borrar realmente: DRYRUN=0 bash scripts/cleanup_backups.sh ${ROOT_DIR}"
  exit 0
fi

echo "⚠️  Procediendo a borrar..."
echo "${CANDIDATES}" | xargs -I{} rm -f "{}"

echo "==> Verificando que ya no existan:"
MISSING=$(echo "${CANDIDATES}" | xargs -I{} test ! -e "{}" && echo "ok" || true)
echo "✔ Limpieza completada."

exit 0
