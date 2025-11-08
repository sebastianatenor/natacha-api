CANONICAL="${NATACHA_CONTEXT_API:-https://natacha-api-mkwskljrhq-uc.a.run.app}"
#!/usr/bin/env bash
set -euo pipefail

REG="knowledge/registry/REGISTRY.md"
mkdir -p "$(dirname "$REG")"

CHECK_NAME="$(gcloud monitoring uptime list-configs --format='value(name)' | head -n1 || true)"
HOST="$( [ -n "$CHECK_NAME" ] && gcloud monitoring uptime describe "$CHECK_NAME" --format='value(monitoredResource.labels.host)' || echo '' )"

{
  echo "# REGISTRY — Natacha Capabilities"
  echo "_Última actualización: $(date '+%Y-%m-%d %H:%M:%S %z')_"
  echo
  echo "## Uptime Check"
  if [ -n "$CHECK_NAME" ]; then
    gcloud monitoring uptime describe "$CHECK_NAME" --format='yaml(name,displayName,monitoredResource,httpCheck,selectedRegions)' || true
  else
    echo "(no uptime check configurado)"
  fi
  echo
  echo "## Alert Policies (Uptime)"
  gcloud alpha monitoring policies list \
    --filter='displayName:"CRun | HealthMonitor | Uptime"' \
    --format='table(name,displayName,enabled)' || true
  echo
  echo "### Detalle"
  for P in $(gcloud alpha monitoring policies list --filter='displayName:"CRun | HealthMonitor | Uptime"' --format='value(name)' || true); do
    echo
    gcloud alpha monitoring policies describe "$P" --format=json \
    | jq '{
        displayName,
        enabled,
        notificationChannels,
        condition: (
          .conditions[0] |
          if has("conditionThreshold") then {
            type:"threshold",
            filter:.conditionThreshold.filter,
            comparison:.conditionThreshold.comparison,
            thresholdValue:(.conditionThreshold.thresholdValue // null),
            duration:.conditionThreshold.duration,
            aggregations:(.conditionThreshold.aggregations // []),
            evaluationMissingData:(.conditionThreshold.evaluationMissingData // "UNSPECIFIED")
          } elif has("conditionMonitoringQueryLanguage") then {
            type:"mql",
            duration:.conditionMonitoringQueryLanguage.duration,
            query:.conditionMonitoringQueryLanguage.query
          } else {type:"other"}
          end
        )
      }'
  done
  echo
  echo "## Notification Channels"
  gcloud alpha monitoring channels list \
    --format='table(name,displayName,type,labels.email_address)' || true
} > "$REG"

echo "🧠 brain_sync: actualizado $REG"
