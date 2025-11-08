#!/usr/bin/env bash
set -euo pipefail

PROJ="${PROJ:-$(gcloud config get-value core/project 2>/dev/null || true)}"
REG="${REG:-$(gcloud config get-value run/region 2>/dev/null || echo us-central1)}"
SVC="${SVC:-natacha-api}"

if [ -z "${PROJ:-}" ]; then
  echo "ERROR: PROJ vacío. Seteá gcloud core/project o pasá PROJ=..." >&2
  exit 1
fi

# Tolerar fallos de gcloud (no romper por -e/-u)
URL="$(gcloud run services describe "$SVC" --project "$PROJ" --region "$REG" --format='value(status.url)' 2>/dev/null || true)"
REV_FULL="$(gcloud run services describe "$SVC" --project "$PROJ" --region "$REG" --format='value(status.latestReadyRevisionName)' 2>/dev/null || true)"
REV_FULL="${REV_FULL:-}"
REV="${REV_FULL##*/}"

IMG=""
if [ -n "${REV:-}" ]; then
  IMG="$(gcloud run revisions describe "$REV" --project "$PROJ" --region "$REG" --format='value(spec.containers[0].image)')" || true
fi
URL="${URL:-}"; IMG="${IMG:-}"

TMP="$(mktemp)"
{
  echo "# Natacha API — REGISTRY"
  echo
  echo "## Servicio"
  echo "- Proyecto: $PROJ"
  echo "- Región: $REG"
  echo "- Servicio: $SVC"
  echo "- URL producción: ${URL:-N/A}"
  echo "- Revisión activa: ${REV:-N/A}"
  echo "- Imagen activa: ${IMG:-N/A}"
  echo
  echo "## Generado"
  echo "- Fecha: $(date -Is)"
  echo "- Fuente de verdad: Cloud Run (status.url, latestReadyRevisionName, image)"
} > "$TMP"

mv "$TMP" "$HOME/REGISTRY.md"
echo "REFRESH OK -> $HOME/REGISTRY.md"
