CANONICAL="${NATACHA_CONTEXT_API:-https://natacha-api-mkwskljrhq-uc.a.run.app}"
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
