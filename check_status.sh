#!/bin/sh

# Crear directorio de logs si no existe
mkdir -p /scripts/logs

LOG_FILE="/scripts/logs/health.log"

echo "🧠 Verificando estado del ecosistema Natacha..." | tee -a "$LOG_FILE"

# API principal
API=$(curl -s http://natacha-api:8080/health | jq -r '.status' 2>/dev/null)
echo "🌐 natacha-api: ${API:-❌ no responde}"
echo "🌐 natacha-api: ${API:-no responde}" >> "$LOG_FILE"

# Core
CORE=$(curl -s http://natacha-core:8080/health | jq -r '.status' 2>/dev/null)
echo "⚙️  natacha-core: ${CORE:-❌ no responde}"
echo "⚙️  natacha-core: ${CORE:-no responde}" >> "$LOG_FILE"

# Memory Console
MEMORY=$(curl -s http://natacha-memory-console:8080/health | jq -r '.response.firestore' 2>/dev/null)
if [ "$MEMORY" = "true" ]; then
  echo "💾 natacha-memory-console: ✅ Firestore conectado"
  echo "💾 natacha-memory-console: Firestore OK" >> "$LOG_FILE"
else
  echo "💾 natacha-memory-console: ❌ no responde o sin Firestore"
  echo "💾 natacha-memory-console: ERROR" >> "$LOG_FILE"
fi

echo "✅ Verificación completada."
