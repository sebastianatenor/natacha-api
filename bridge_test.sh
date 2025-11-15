#!/bin/bash
# ===========================================================
# 🔗 Prueba de integración entre Natacha API (8080) y Core (8081)
# ===========================================================

echo "──────────────────────────────────────────────"
echo "🔍 Verificando estado de los servicios locales..."
echo "──────────────────────────────────────────────"

API_URL="http://localhost:8080"
CORE_URL="http://localhost:8081"

check_service() {
  local url=$1
  local name=$2
  echo -n "→ Chequeando $name en $url ... "
  if curl -s --connect-timeout 3 "$url/health" | grep -q '"status"'; then
    echo "✅ OK"
  else
    echo "❌ No responde"
  fi
}

check_service "$API_URL" "API principal"
check_service "$CORE_URL" "Core cognitivo"

echo "──────────────────────────────────────────────"
echo "🧠 Enviando mensaje al Core vía API de prueba..."
echo "──────────────────────────────────────────────"

curl -s -X POST "$CORE_URL/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hola Natacha, integración local funcionando"}' | jq

echo "──────────────────────────────────────────────"
echo "✅ Prueba completada."
