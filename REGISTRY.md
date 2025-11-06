# 🧭 REGISTRY – Proyecto Natacha (Snapshot 20251106T233555Z UTC)

## 📦 Proyecto GCP
- **Project ID:** asistente-sebastian
- **Número:** 422255208682
- **Región principal:** us-central1

## ☁️ Cloud Run – Servicios activos
```yaml
---
metadata:
  name: auto-stop-vm
status:
  latestCreatedRevisionName: auto-stop-vm-00001-qec
  traffic:
  - latestRevision: true
    percent: 100
    revisionName: auto-stop-vm-00001-qec
  url: https://auto-stop-vm-mkwskljrhq-uc.a.run.app
---
metadata:
  name: autostart-vm
status:
  latestCreatedRevisionName: autostart-vm-00003-dov
  traffic:
  - latestRevision: true
    percent: 100
    revisionName: autostart-vm-00003-dov
  url: https://autostart-vm-mkwskljrhq-uc.a.run.app
---
metadata:
  name: log-natacha-activity
status:
  latestCreatedRevisionName: log-natacha-activity-00001-bev
  traffic:
  - latestRevision: true
    percent: 100
    revisionName: log-natacha-activity-00001-bev
  url: https://log-natacha-activity-mkwskljrhq-uc.a.run.app
---
metadata:
  name: natacha-api
status:
  latestCreatedRevisionName: natacha-api-00264-8lg
  traffic:
  - latestRevision: true
    percent: 100
    revisionName: natacha-api-00263-cdr
  - revisionName: natacha-api-00317-qip
    tag: health-test
    url: https://health-test---natacha-api-mkwskljrhq-uc.a.run.app
  url: https://natacha-api-mkwskljrhq-uc.a.run.app
---
metadata:
  name: natacha-api-a
status:
  latestCreatedRevisionName: natacha-api-a-00050-655
  traffic:
  - percent: 100
    revisionName: natacha-api-a-00050-655
  url: https://natacha-api-a-mkwskljrhq-uc.a.run.app
---
metadata:
  name: natacha-api-stable
status:
  latestCreatedRevisionName: natacha-api-stable-00001-758
  traffic:
  - latestRevision: true
    percent: 100
    revisionName: natacha-api-stable-00001-758
  url: https://natacha-api-stable-mkwskljrhq-uc.a.run.app
---
metadata:
  name: natacha-api-stg
status:
  latestCreatedRevisionName: natacha-api-stg-00006-2db
  traffic:
  - latestRevision: true
    percent: 100
    revisionName: natacha-api-stg-00006-2db
  url: https://natacha-api-stg-mkwskljrhq-uc.a.run.app
---
metadata:
  name: natacha-command-endpoint
status:
  latestCreatedRevisionName: natacha-command-endpoint-00001-wgt
  traffic:
  - latestRevision: true
    percent: 100
    revisionName: natacha-command-endpoint-00001-wgt
  url: https://natacha-command-endpoint-mkwskljrhq-uc.a.run.app
---
metadata:
  name: natacha-core
status:
  latestCreatedRevisionName: natacha-core-00042-lgr
  traffic:
  - latestRevision: true
    percent: 100
    revisionName: natacha-core-00042-lgr
  url: https://natacha-core-mkwskljrhq-uc.a.run.app
---
metadata:
  name: natacha-dashboard
status:
  latestCreatedRevisionName: natacha-dashboard-00007-rd7
  traffic:
  - latestRevision: true
    percent: 100
    revisionName: natacha-dashboard-00007-rd7
  url: https://natacha-dashboard-mkwskljrhq-uc.a.run.app
---
metadata:
  name: natacha-health-monitor
status:
  latestCreatedRevisionName: natacha-health-monitor-00033-mct
  traffic:
  - latestRevision: true
    percent: 100
    revisionName: natacha-health-monitor-00033-mct
  url: https://natacha-health-monitor-mkwskljrhq-uc.a.run.app
---
metadata:
  name: natacha-memory-console
status:
  latestCreatedRevisionName: natacha-memory-console-00076-v7c
  traffic:
  - latestRevision: true
    percent: 100
    revisionName: natacha-memory-console-00076-v7c
  url: https://natacha-memory-console-mkwskljrhq-uc.a.run.app
---
metadata:
  name: natacha-plugin-registry
status:
  latestCreatedRevisionName: natacha-plugin-registry-00004-dc4
  traffic:
  - latestRevision: true
    percent: 100
    revisionName: natacha-plugin-registry-00004-dc4
  url: https://natacha-plugin-registry-mkwskljrhq-uc.a.run.app
---
metadata:
  name: natacha-whatsapp
status:
  latestCreatedRevisionName: natacha-whatsapp-00006-p2w
  traffic:
  - latestRevision: true
    percent: 100
    revisionName: natacha-whatsapp-00006-p2w
  url: https://natacha-whatsapp-mkwskljrhq-uc.a.run.app
---
metadata:
  name: natachaspeak
status:
  latestCreatedRevisionName: natachaspeak-00013-b4b
  traffic:
  - latestRevision: true
    percent: 100
    revisionName: natachaspeak-00013-b4b
  url: https://natachaspeak-mkwskljrhq-uc.a.run.app
---
metadata:
  name: stop-natacha-vm
status:
  latestCreatedRevisionName: stop-natacha-vm-00001-faz
  traffic:
  - latestRevision: true
    percent: 100
    revisionName: stop-natacha-vm-00001-faz
  url: https://stop-natacha-vm-mkwskljrhq-uc.a.run.app
---
metadata:
  name: vm-proxy
status:
  latestCreatedRevisionName: vm-proxy-00002-lef
  traffic:
  - latestRevision: true
    percent: 100
    revisionName: vm-proxy-00002-lef
  url: https://vm-proxy-mkwskljrhq-uc.a.run.app
```

## 🌍 Dominios personalizados
```yaml
### api.llvc-global.com
metadata:
  creationTimestamp: '2025-11-06T20:57:37.222507Z'
status:
  conditions:
  - lastTransitionTime: '2025-11-06T21:53:51.596485Z'
    status: 'True'
    type: Ready
  - lastTransitionTime: '2025-11-06T21:53:51.596485Z'
    status: 'True'
    type: CertificateProvisioned
  - lastTransitionTime: '2025-11-06T20:57:43.209085Z'
    status: 'True'
    type: DomainRoutable

### dashboard.llvc-global.com
metadata:
  creationTimestamp: '2025-11-06T20:57:46.816080Z'
status:
  conditions:
  - lastTransitionTime: '2025-11-06T21:54:04.220751Z'
    status: 'True'
    type: Ready
  - lastTransitionTime: '2025-11-06T21:54:04.220751Z'
    status: 'True'
    type: CertificateProvisioned
  - lastTransitionTime: '2025-11-06T20:57:54.342698Z'
    status: 'True'
    type: DomainRoutable

```

## 🔐 Service Accounts relevantes
```yaml
---
disabled: false
displayName: Natacha Scheduler SA
email: natacha-scheduler-sa@asistente-sebastian.iam.gserviceaccount.com
---
disabled: false
displayName: Natacha Cloud Executor
email: natacha-cloud-executor@asistente-sebastian.iam.gserviceaccount.com
---
disabled: false
displayName: natacha-firestore-access
email: natacha-firestore-access@asistente-sebastian.iam.gserviceaccount.com
---
disabled: false
displayName: GitHub Actions for Natacha
email: natacha-github@asistente-sebastian.iam.gserviceaccount.com
---
disabled: false
displayName: Natacha Service Checker
email: natacha-checker@asistente-sebastian.iam.gserviceaccount.com
---
disabled: false
displayName: natacha-service
email: natacha-service@asistente-sebastian.iam.gserviceaccount.com
---
disabled: false
displayName: natacha-memory-console
email: natacha-memory-console@asistente-sebastian.iam.gserviceaccount.com
---
disabled: false
displayName: natacha-service
email: natacha-service-172@asistente-sebastian.iam.gserviceaccount.com
---
disabled: false
displayName: Natacha Automation
email: natacha-automation@asistente-sebastian.iam.gserviceaccount.com
```

## 🔑 Secrets en uso
```yaml
---
name: projects/422255208682/secrets/AD_NUM
---
name: projects/422255208682/secrets/API_KEY
---
name: projects/422255208682/secrets/BUSINESS_ID
---
name: projects/422255208682/secrets/IMG_ID
---
name: projects/422255208682/secrets/META_ACCESS_TOKEN
---
name: projects/422255208682/secrets/META_TOKEN
---
name: projects/422255208682/secrets/META_WHATSAPP_TOKEN
---
name: projects/422255208682/secrets/NATACHA_TOKEN
---
name: projects/422255208682/secrets/NOTION_TOKEN
---
name: projects/422255208682/secrets/PAGE_ID
---
name: projects/422255208682/secrets/PAGE_TOKEN
---
name: projects/422255208682/secrets/PHONE_NUMBER_ID
---
name: projects/422255208682/secrets/SERVICE_ACCOUNT_KEY
---
name: projects/422255208682/secrets/SLACK_WEBHOOK
---
name: projects/422255208682/secrets/WABA
---
name: projects/422255208682/secrets/natacha-api-key
---
name: projects/422255208682/secrets/natacha-firestore-key
```

## 🪵 Logging y Monitoring
- Logging habilitado: Cloud Logging (roles/logging.viewer asignado)
- Stackdriver Monitoring: roles/monitoring.viewer activo

## 🧰 Último build fallido
- ID: 566f0b03-5925-4488-b6ea-45ff86c6971b
- URL: https://console.cloud.google.com/cloud-build/builds;region=us-central1/566f0b03-5925-4488-b6ea-45ff86c6971b?project=422255208682

## 🗺️ Infraestructura relacionada
- **Repositorio:** ~/natacha-api
- **Branch actual:** main
- **Último commit:** 2839ecc fix(registry): actualizar URL canónica a https://natacha-api-mkwskljrhq-uc.a.run.app
- **Backup del Dockerfile:** Dockerfile.bak.1762471607
- **Backup de requirements:** requirements.txt.bak.1762471607

## 🧩 Estado general
- API: ✅ en producción (revisión estable responde en /health)
- Dashboard: ✅ dominio activo y HTML sirviendo
- Último deploy fallido: contenedor no escuchó $PORT=8080 (sin impacto en tráfico)
- Siguiente paso: implementar **memoria del agente (Firestore)**
