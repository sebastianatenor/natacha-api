#!/bin/bash
# shellcheck disable=SC2034  # variable reservada para estilos/emoji
# shellcheck disable=SC2034  # variable reservada / uso indirecto
set -e

# === 🎨 COLORES Y EMOJIS ===
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
CHECK="✅"
CROSS="❌"
WARN="⚠️"
GEAR="⚙️"
BRAIN="🧠"
DISK="💾"
GLOBE="🌐"
ROCKET="🚀"

# === 🕒 CONFIGURACIÓN INICIAL ===
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="$HOME/Projects/natacha-api/logs"
LOG_FILE="$LOG_DIR/deploy_log_$TIMESTAMP.txt"
mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

echo -e "${BLUE}$ROCKET Iniciando despliegue Natacha ($TIMESTAMP)...${NC}"
echo "=============================================================="

# === 1️⃣ LIMPIEZA ===
echo -e "${YELLOW}🧹 Limpiando contenedores previos...${NC}"
docker compose down -v --remove-orphans >/dev/null 2>&1 || true

# === 2️⃣ CONSTRUCCIÓN Y LEVANTAMIENTO ===
echo -e "${BLUE}$GEAR Reconstruyendo servicios...${NC}"
docker compose up --build -d

# === 3️⃣ ESPERA ===
echo -e "${YELLOW}⏳ Esperando inicialización (10s)...${NC}"
sleep 10

# === 4️⃣ FUNCIONES DE CHEQUEO ===
check_service() {
  local name=$1
  local url=$2
  local icon=$3
  local result
  result=$(curl -s -o /dev/null -w "%{http_code}" "$url" || true)

  if [ "$result" == "200" ]; then
    echo -e "$icon ${GREEN}$name: OK $CHECK${NC}"
    return 0
  else
    echo -e "$icon ${RED}$name: ERROR $CROSS (${result:-no response})${NC}"
    return 1
  fi
}

# === 5️⃣ CHEQUEO DE SERVICIOS ===
echo ""
echo -e "${BRAIN} Verificando estado de los microservicios..."
echo "------------------------------------------------"

check_service "API" "http://localhost:8080/health" "$GLOBE"
api_status=$?

check_service "CORE" "http://localhost:8081/health" "$GEAR"
core_status=$?

check_service "MEMORY" "http://localhost:8082/health" "$DISK"
memory_status=$?

# === 6️⃣ TEST AUTOMÁTICO DE MEMORIA ===
echo ""
echo -e "${DISK} Prueba automática de memoria (store + get)..."
STORE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"key": "auto_test", "value": "sincronizado"}' \
  http://localhost:8080/memory/store | jq -r '.memory_status' 2>/dev/null || echo "error")

if [[ "$STORE" == "ok" ]]; then
  echo -e "   ${GREEN}Store OK${NC}"
else
  echo -e "   ${RED}Error en /memory/store${NC}"
fi

GET=$(curl -s http://localhost:8080/memory/get/auto_test | jq -r '.memory_status' 2>/dev/null || echo "error")
if [[ "$GET" == "ok" ]]; then
  echo -e "   ${GREEN}Get OK${NC}"
else
  echo -e "   ${RED}Error en /memory/get${NC}"
fi

# === 7️⃣ RESUMEN FINAL ===
echo ""
echo "=============================================================="
echo -e "${BLUE}📊 RESUMEN DEL DESPLIEGUE:${NC}"

printf "   %-20s %s\n" "🌐 API" "$( [ $api_status -eq 0 ] && echo -e "${GREEN}OK${NC}" || echo -e "${RED}ERROR${NC}")"
printf "   %-20s %s\n" "⚙️  CORE" "$( [ $core_status -eq 0 ] && echo -e "${GREEN}OK${NC}" || echo -e "${RED}ERROR${NC}")"
printf "   %-20s %s\n" "💾 MEMORY" "$( [ $memory_status -eq 0 ] && echo -e "${GREEN}OK${NC}" || echo -e "${RED}ERROR${NC}")"

echo ""
echo -e "${GREEN}$CHECK Despliegue completado exitosamente${NC}"
echo -e "${YELLOW}🗂️  Log guardado en: $LOG_FILE${NC}"
echo "=============================================================="
