# REGISTRY — Natacha Capabilities
_Última actualización: 2025-10-29 19:28:50 -0300_

## Uptime Check
displayName: HealthMonitor /
httpCheck:
  path: /
  port: 443
  requestMethod: GET
  useSsl: true
monitoredResource:
  labels:
    host: natacha-health-monitor-422255208682.us-central1.run.app
    project_id: asistente-sebastian
  type: uptime_url
name: projects/asistente-sebastian/uptimeCheckConfigs/healthmonitor-mertgzh6hJg

## Alert Policies (Uptime)
NAME                                                             DISPLAY_NAME                                      ENABLED
projects/asistente-sebastian/alertPolicies/13575294913821338865  CRun | HealthMonitor | Uptime / all regions down  True
projects/asistente-sebastian/alertPolicies/5980311962589578804   CRun | HealthMonitor | Uptime / down              True

### Detalle

{
  "displayName": "CRun | HealthMonitor | Uptime / all regions down",
  "enabled": true,
  "notificationChannels": [
    "projects/asistente-sebastian/notificationChannels/17012733904319805436"
  ],
  "condition": {
    "type": "threshold",
    "filter": "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\" AND resource.label.\"host\"=\"natacha-health-monitor-422255208682.us-central1.run.app\"",
    "comparison": "COMPARISON_LT",
    "thresholdValue": null,
    "duration": "120s",
    "aggregations": [
      {
        "alignmentPeriod": "60s",
        "perSeriesAligner": "ALIGN_NEXT_OLDER"
      },
      {
        "alignmentPeriod": "60s",
        "crossSeriesReducer": "REDUCE_COUNT_TRUE"
      }
    ],
    "evaluationMissingData": "EVALUATION_MISSING_DATA_INACTIVE"
  }
}

{
  "displayName": "CRun | HealthMonitor | Uptime / down",
  "enabled": true,
  "notificationChannels": [
    "projects/asistente-sebastian/notificationChannels/17012733904319805436"
  ],
  "condition": {
    "type": "threshold",
    "filter": "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\" AND resource.label.\"host\"=\"natacha-health-monitor-422255208682.us-central1.run.app\"",
    "comparison": "COMPARISON_LT",
    "thresholdValue": 1.0,
    "duration": "120s",
    "aggregations": [
      {
        "alignmentPeriod": "60s",
        "perSeriesAligner": "ALIGN_NEXT_OLDER"
      }
    ],
    "evaluationMissingData": "EVALUATION_MISSING_DATA_INACTIVE"
  }
}

## Notification Channels
NAME                                                                    DISPLAY_NAME                   TYPE   EMAIL_ADDRESS
projects/asistente-sebastian/notificationChannels/16131789610057042414  Notificaciones Meta Token      email  sebastianatenor@gmail.com
projects/asistente-sebastian/notificationChannels/17012733904319805436  Alertas LLVC Global - Natacha  email  sebastianatenor@gmail.com
projects/asistente-sebastian/notificationChannels/306082373074028591    Seba Email                     email  sebastianatenor@gmail.com
projects/asistente-sebastian/notificationChannels/5941256893092102238   Ops Alerts (Seba)              email  sebastianatenor@gmail.com
