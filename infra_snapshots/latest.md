# Natacha – Daily Digest (20251029T002906)

- Proyecto: asistente-sebastian
- Región: us-central1
- Host: Darwin MacBook-Air-de-Alvaro.local 24.6.0 Darwin Kernel Version 24.6.0: Mon Aug 11 21:16:52 PDT 2025; root:xnu-11417.140.69.701.11~1/RELEASE_ARM64_T8112 arm64 

## Resumen rápido

- Servicios Cloud Run: 14
- Jobs Scheduler: 15
- Métricas Logging: sí
- Políticas Monitoring: 4

## Servicios Cloud Run
- auto-stop-vm -> https://auto-stop-vm-mkwskljrhq-uc.a.run.app
- autostart-vm -> https://autostart-vm-mkwskljrhq-uc.a.run.app
- log-natacha-activity -> https://log-natacha-activity-mkwskljrhq-uc.a.run.app
- natacha-api -> https://natacha-api-mkwskljrhq-uc.a.run.app
- natacha-command-endpoint -> https://natacha-command-endpoint-mkwskljrhq-uc.a.run.app
- natacha-core -> https://natacha-core-mkwskljrhq-uc.a.run.app
- natacha-dashboard -> https://natacha-dashboard-mkwskljrhq-uc.a.run.app
- natacha-health-monitor -> https://natacha-health-monitor-mkwskljrhq-uc.a.run.app
- natacha-memory-console -> https://natacha-memory-console-mkwskljrhq-uc.a.run.app
- natacha-plugin-registry -> https://natacha-plugin-registry-mkwskljrhq-uc.a.run.app
- natacha-whatsapp -> https://natacha-whatsapp-mkwskljrhq-uc.a.run.app
- natachaspeak -> https://natachaspeak-mkwskljrhq-uc.a.run.app
- stop-natacha-vm -> https://stop-natacha-vm-mkwskljrhq-uc.a.run.app
- vm-proxy -> https://vm-proxy-mkwskljrhq-uc.a.run.app

## Scheduler (jobs)
- auto-heal-monitor-job @ */15 * * * * [ENABLED]
- health-daily @ 0 9 * * * [ENABLED]
- llvc-backup-daily @ 0 2 * * * [ENABLED]
- natacha-auto-infra-check @ 0 */2 * * * [ENABLED]
- natacha-health-check-hourly @ 30 * * * * [ENABLED]
- natacha-self-heal-6h @ 0 */6 * * * [ENABLED]
- natacha-smart-health @ */5 * * * * [ENABLED]
- natacha-snapshot-hourly @ 0 * * * * [ENABLED]
- natacha-verifyops-hourly @ 15 * * * * [ENABLED]
- renew-meta-token-job @ 0 3 * * * [ENABLED]
- run-auto-heal @ */15 * * * * [ENABLED]
- scheduler-health-check @ 0 */6 * * * [ENABLED]
- test-natacha-api @ 0 */6 * * * [ENABLED]
- verify-daily-flow @ 30 18 * * * [ENABLED]
- verify-pubsub-flow-daily @ 45 18 * * * [ENABLED]

## Últimos logs (-1h)

## IAM (Run invoker/viewer)

### roles/run.invoker

### roles/run.viewer

## Secrets (names)
- projects/422255208682/secrets/AD_NUM
- projects/422255208682/secrets/API_KEY
- projects/422255208682/secrets/BUSINESS_ID
- projects/422255208682/secrets/IMG_ID
- projects/422255208682/secrets/META_ACCESS_TOKEN
- projects/422255208682/secrets/META_TOKEN
- projects/422255208682/secrets/META_WHATSAPP_TOKEN
- projects/422255208682/secrets/NATACHA_TOKEN
- projects/422255208682/secrets/NOTION_TOKEN
- projects/422255208682/secrets/PAGE_ID
- projects/422255208682/secrets/PAGE_TOKEN
- projects/422255208682/secrets/PHONE_NUMBER_ID
- projects/422255208682/secrets/SERVICE_ACCOUNT_KEY
- projects/422255208682/secrets/SLACK_WEBHOOK
- projects/422255208682/secrets/WABA
