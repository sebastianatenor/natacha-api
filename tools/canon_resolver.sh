#!/usr/bin/env bash
# Uso:
#   source tools/canon_resolver.sh
#   resolve_canon   # exporta CANONICAL
set -euo pipefail

resolve_canon() {
  # 1) prioridad a env
  if [ -n "${NATACHA_CONTEXT_API:-}" ]; then
    export CANONICAL="$NATACHA_CONTEXT_API"
    return
  fi
  if [ -n "${CANON:-}" ]; then
    export CANONICAL="$CANON"
    return
  fi
  # 2) Cloud Run status.url
  local PROJ REG SVC
  PROJ="${PROJ:-$(gcloud config get-value core/project 2>/dev/null || true)}"
  REG="${REG:-$(gcloud config get-value run/region 2>/dev/null || echo us-central1)}"
  SVC="${SVC:-natacha-api}"
  if URL="$(gcloud run services describe "$SVC" --project "$PROJ" --region "$REG" --format='value(status.url)' 2>/dev/null)"; then
    if [ -n "$URL" ]; then
      export CANONICAL="$URL"
      return
    fi
  fi
  # 3) Fallback a REGISTRY.md
  if [ -f "$HOME/REGISTRY.md" ]; then
    URL="$(sed -n 's/^- URL producción: *//p' "$HOME/REGISTRY.md" | head -n1)"
    if [ -n "$URL" ]; then
      export CANONICAL="$URL"
      return
    fi
  fi
  # 4) último recurso: vacío (dejar que el caller maneje el error)
  export CANONICAL=""
}
