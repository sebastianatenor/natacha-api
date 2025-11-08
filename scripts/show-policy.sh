. "$(dirname "$0")/../tools/canon_resolver.sh" || source tools/canon_resolver.sh
resolve_canon # exporta CANONICAL
#!/usr/bin/env bash
set -euo pipefail
PID="${1:-projects/asistente-sebastian/alertPolicies/6323746048274976644}"

echo "🔎 Policy: $PID"
gcloud alpha monitoring policies describe "$PID" --format=json \
| jq '{
    name,
    displayName,
    enabled,
    notificationChannels,
    userLabels,
    documentation: { mimeType: .documentation.mimeType }
  }'
