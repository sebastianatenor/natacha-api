#!/usr/bin/env bash
set -euo pipefail

# === Config ===
PROJECT="${PROJECT:-asistente-sebastian}"
REGION="${REGION:-us-central1}"
SVC="${SVC:-natacha-api}"
DRY="${DRY:-0}"   # export DRY=1 para ver sin aplicar

echo "== Recovery start =="
echo "PROJECT=$PROJECT  REGION=$REGION  SVC=$SVC  DRY=$DRY"

# === Preflight: binarios ===
command -v gcloud >/dev/null || { echo "❌ gcloud no disponible"; exit 1; }
command -v jq >/dev/null || { echo "❌ jq no disponible"; exit 1; }
command -v curl >/dev/null || { echo "❌ curl no disponible"; exit 1; }

# === Descubrir estado real en Cloud Run ===
CR_URL="$(gcloud run services describe "$SVC" --project "$PROJECT" --region "$REGION" \
  --format='value(status.url)')"
LATEST_READY="$(gcloud run services describe "$SVC" --project "$PROJECT" --region "$REGION" \
  --format='value(status.latestReadyRevisionName)')"

if [[ -z "${CR_URL}" || -z "${LATEST_READY}" ]]; then
  echo "❌ No pude obtener URL o latestReadyRevisionName"
  exit 1
fi

echo "🔎 Cloud Run: URL=${CR_URL}"
echo "🔎 Cloud Run: latestReady=${LATEST_READY}"

# === Health checks (no fallan el script si /health da 404) ===
echo "→ Probar /health: ${CR_URL}/health"
set +e
HC_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${CR_URL}/health")
set -e
echo "   /health code: ${HC_CODE}"

echo "→ Probar __whoami"
set +e
WHOAMI_JSON=$(curl -s "${CR_URL}/__whoami")
set -e
if [[ -n "${WHOAMI_JSON}" ]]; then
  echo "${WHOAMI_JSON}" | jq . 2>/dev/null || echo "${WHOAMI_JSON}"
else
  echo "   (sin respuesta)"
fi

# === Sincronizar REGISTRY.md ===
if [[ ! -f REGISTRY.md ]]; then
  echo "⚠️  No existe REGISTRY.md, lo creo base"
  cat > REGISTRY.md <<EOF
- URL: ${CR_URL}
- Revisión: ${LATEST_READY}
- Service Account: (completar si aplica)
- Secret montado: (completar si aplica)
EOF
  CHANGED=1
else
  # Guardar copia y reescribir solo si difiere
  CURRENT_URL="$(grep '^- URL:' REGISTRY.md | awk '{print $3}')"
  CURRENT_REV="$(grep '^- Revisión:' REGISTRY.md | awk '{print $3}')"

  echo "📘 REGISTRY.md -> URL=${CURRENT_URL:-<vacío>}  REV=${CURRENT_REV:-<vacío>}"

  CHANGED=0

  if [[ "${CURRENT_URL:-}" != "${CR_URL}" ]]; then
    echo "↺ Actualizando URL en REGISTRY.md"
    [[ "$DRY" == "1" ]] || sed -i.bak -E "s|^- URL:.*|- URL: ${CR_URL}|" REGISTRY.md
    CHANGED=1
  fi

  if [[ "${CURRENT_REV:-}" != "${LATEST_READY}" ]]; then
    echo "↺ Actualizando Revisión en REGISTRY.md"
    [[ "$DRY" == "1" ]] || sed -i.bak -E "s|^- Revisión:.*|- Revisión: ${LATEST_READY}|" REGISTRY.md
    CHANGED=1
  fi
fi

# === Re-chequeo de salud con el checker propio (si existe) ===
if [[ -f scripts/registry_check.py ]]; then
  echo "→ Ejecutando scripts/registry_check.py"
  [[ "$DRY" == "1" ]] || python3 scripts/registry_check.py || true
else
  echo "ℹ️  No encontré scripts/registry_check.py (ok, continúo)"
fi

# === Git commit si hubo cambios ===
if [[ "${CHANGED}" == "1" && "$DRY" != "1" ]]; then
  echo "→ Haciendo commit de REGISTRY.md"
  git add REGISTRY.md || true
  git commit -m "chore(recovery): sincronizar REGISTRY.md con Cloud Run (URL=${CR_URL}, rev=${LATEST_READY})" || true
else
  echo "✓ No hay cambios que commitear" 
fi

echo "== Recovery done ✅ =="
