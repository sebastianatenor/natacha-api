CANONICAL="${NATACHA_CONTEXT_API:-https://natacha-api-mkwskljrhq-uc.a.run.app}"
#!/usr/bin/env bash
set -euo pipefail

# Uso:
#  scripts/cap_preflight.sh uptime           # solo uptime/policies
#  scripts/cap_preflight.sh file path/algo  # preflight de archivo local

case "${1:-}" in
  uptime)
    echo "🔎 Preflight Uptime/Policies…"
    # Uptime
    CHECK="$(gcloud monitoring uptime list-configs --format='value(name)' 2>/dev/null | head -n1 || true)"
    if [ -n "$CHECK" ]; then
      echo "  ✅ Uptime check ya existe: $CHECK"
    else
      echo "  ⚠️  No hay uptime check (ok si lo vas a crear)."
    fi
    # Policies (por displayName)
    gcloud alpha monitoring policies list \
      --filter='displayName:"CRun | HealthMonitor | Uptime"' \
      --format='table(name,displayName,enabled)' 2>/dev/null || true
    ;;
  file)
    TARGET="${2:-}"
    if [ -z "$TARGET" ]; then echo "Uso: $0 file <ruta>"; exit 2; fi
    if [ -e "$TARGET" ]; then
      echo "⛔ Preflight: ya existe $TARGET"; head -n 20 "$TARGET" || true; exit 3
    else
      echo "✅ Preflight OK: no existe $TARGET"
    fi
    ;;
  *)
    echo "Uso: $0 {uptime|file <ruta>}"; exit 2;
    ;;
esac
