# REGISTRY.md (core)

Service: natacha-api-a
Canonical URL: https://natacha-api-a-422255208682.us-central1.run.app
Latest Ready Revision: natacha-api-a-00038-yaf
Image: us-central1-docker.pkg.dev/asistente-sebastian/cloud-run-source-deploy/natacha-api-a@sha256:4f1f5e08975c51a566be0d0950d1ab78188412c3f0cdc66ad0586e6c279ea2ee
Service Account (runtime): natacha-firestore-access@asistente-sebastian.iam.gserviceaccount.com

Guías:
- Producción SOLO usa la Canonical URL.
- Servicios privados: invocación con ID token (user) o SA autorizado.
- Cualquier URL distinta a la canónica => bloquear en pre-commit.
Snapshot OpenAPI: openapi_snapshots/openapi_20251106T012313.json
