# Baseline · Natacha API

Este baseline contiene:
- `cloudbuild.yaml`: pipeline reproducible, con substitutions válidas (`_VAR`).
- `policies/`: políticas MQL (error rate, p95 latency, no-traffic/0-instances).
- `scripts/`: preflight de servicio y chequeos rápidos.
- `make/Makefile`: atajos para preflight/build/push/deploy/health.

## Aplicar políticas
```bash
gcloud monitoring policies create --policy-from-file=baseline/policies/error-rate.json
gcloud monitoring policies create --policy-from-file=baseline/policies/latency-p95.json
gcloud monitoring policies create --policy-from-file=baseline/policies/no-traffic-or-0-instances.json
