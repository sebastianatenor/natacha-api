#!/bin/bash
set -e

echo "🚀 === DIAGNÓSTICO DE INFRAESTRUCTURA NATACHA ==="
DATE=$(date)
OUTPUT_FILE="/tmp/infra_status.json"

echo "Fecha: $DATE"
echo "-----------------------------------------------"

# Detectar si estamos en Cloud Run o en local
if [ -n "$K_SERVICE" ]; then
  ENVIRONMENT="cloudrun"
else
  ENVIRONMENT="local"
fi

# 🔹 INFO BÁSICA
PROJECT=$(gcloud config get-value project 2>/dev/null || echo "N/A")
ACCOUNT=$(gcloud config get-value account 2>/dev/null || echo "N/A")

# 🔹 VM STATUS
if [ "$ENVIRONMENT" = "local" ]; then
  VM_STATUS=$(gcloud compute instances list --format="json" 2>/dev/null || echo "[]")
else
  VM_STATUS="[]"
fi

# 🔹 DOCKER CONTAINERS
if command -v docker &>/dev/null; then
  DOCKER_CONTAINERS=$(docker ps --format '{{json .}}' | jq -s '.' 2>/dev/null || echo "[]")
else
  DOCKER_CONTAINERS="[]"
fi

# 🔹 CLOUD RUN SERVICES
CLOUD_RUN=$(gcloud run services list --format="json" --region=us-central1 2>/dev/null || echo "[]")

# 🔹 DISK USAGE
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}')

# 🔹 ARMAMOS JSON
cat <<EOF > "$OUTPUT_FILE"
{
  "timestamp": "$DATE",
  "environment": "$ENVIRONMENT",
  "project": "$PROJECT",
  "account": "$ACCOUNT",
  "vm_status": $VM_STATUS,
  "docker_containers": $DOCKER_CONTAINERS,
  "cloud_run_services": $CLOUD_RUN,
  "disk_usage": "$DISK_USAGE"
}
EOF

echo "✅ Archivo generado: $OUTPUT_FILE"
echo "✅ Diagnóstico completo."
