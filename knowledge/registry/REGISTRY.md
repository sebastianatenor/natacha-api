# REGISTRY — Natacha (auto-generado)
_Última actualización: 2025-10-29 22:01:05Z_

## Uptime & Alerting
- **Uptime Check**: `projects/asistente-sebastian/uptimeCheckConfigs/healthmonitor-mertgzh6hJg`
  - Host: `natacha-health-monitor-422255208682.us-central1.run.app`

### Alert Policies (Uptime)
```
NAME                                                             DISPLAY_NAME                                      ENABLED
projects/asistente-sebastian/alertPolicies/13575294913821338865  CRun | HealthMonitor | Uptime / all regions down  True
projects/asistente-sebastian/alertPolicies/5980311962589578804   CRun | HealthMonitor | Uptime / down              True
```

### Snapshots locales
```
infra_snapshots/alerts/metric-health-monitor-5xx.prod.json
infra_snapshots/alerts/policy-5xx.prod.json
infra_snapshots/alerts/policy-5xx.with-channel.json
infra_snapshots/alerts/policy-5xx.with-doc.json
infra_snapshots/alerts/policy-5xx.with-labels.json
infra_snapshots/alerts/policy-uptime.all-regions.json
infra_snapshots/alerts/policy-uptime.by-host.json
```

## Dashboards
Archivos encontrados:
```
dashboard.py
dashboard/__init__.py
dashboard/dashboard.py
dashboard/dashboard_prod.py
dashboard/infra_control.py
dashboard/infra_control/__init__.py
dashboard/infra_control/auto_healer_panel.py
dashboard/infra_control/cloud_monitor.py
dashboard/infra_control/docker_monitor.py
dashboard/infra_control/infra_audit.py
dashboard/infra_control/system.py
dashboard/infra_history_view.py
dashboard/infrastructure_dashboard.py
dashboard/system_health.py
```

## Notas
- Aplicar **preflight** antes de crear archivos/capacidades nuevas.
- Priorizar **actualizar lo existente** sobre crear duplicados.
