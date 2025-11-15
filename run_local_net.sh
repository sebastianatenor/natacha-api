#!/bin/bash
# ===========================================================
# 🚀 Ejecuta Natacha API en red compartida con el Core Cognitivo
# ===========================================================

docker network inspect natacha-net >/dev/null 2>&1 || docker network create natacha-net

docker run --network natacha-net \
  -p 8080:8080 \
  -v ~/.config/gcloud/application_default_credentials.json:/root/.config/gcloud/application_default_credentials.json \
  -e GOOGLE_CLOUD_PROJECT=asistente-sebastian \
  natacha-brain-local
