#!/usr/bin/env bash
set -e

echo "🚀 Iniciando despliegue inteligente del ecosistema Natacha..."
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/deploy_log_${TIMESTAMP}.txt"

FAST_MODE=false
if [[ "$1" == "--fast" ]]; then
  FAST_MODE=true
fi

echo "📦 Log guardado en: $LOG_FILE"
echo "⏱️  $(date)" | tee -a "$LOG_FILE"

# --- FUNCIONES ---
calculate_checksum() {
  find "$1" -type f -not -path "*/__pycache__/*" -exec md5sum {} \; | md5sum | awk '{ print $1 }'
}

rebuild_service() {
  local service=$1
  echo "🔧 Reconstruyendo $service..." | tee -a "$LOG_FILE"
  docker compose build $service >> "$LOG_FILE" 2>&1
}

# --- INICIO ---
if [ "$FAST_MODE" = true ]; then
  echo "⚡ Modo rápido activado (sin reconstrucción)" | tee -a "$LOG_FILE"
  docker compose up -d >> "$LOG_FILE" 2>&1
else
  declare -A services=(
    ["natacha-api"]="natacha-api"
    ["natacha-core"]="natacha_core"
    ["natacha-memory-console"]="memory_console"
  )

  mkdir -p .checksums
  rebuild_list=()

  for service in "${!services[@]}"; do
    path="${services[$service]}"
    current_sum=$(calculate_checksum "$path")
    checksum_file=".checksums/${service}.sum"

    if [[ ! -f "$checksum_file" || "$current_sum" != "$(cat "$checksum_file")" ]]; then
      echo "$current_sum" > "$checksum_file"
      rebuild_list+=("$service")
    fi
  done

  if [[ ${#rebuild_list[@]} -eq 0 ]]; then
    echo "✅ Sin cambios detectados. Iniciando contenedores existentes..." | tee -a "$LOG_FILE"
    docker compose up -d >> "$LOG_FILE" 2>&1
  else
    echo "🧱 Servicios modificados: ${rebuild_list[*]}" | tee -a "$LOG_FILE"
    docker compose down -v --remove-orphans >> "$LOG_FILE" 2>&1
    for svc in "${rebuild_list[@]}"; do
      rebuild_service "$svc"
    done
    docker compose up -d >> "$LOG_FILE" 2>&1
  fi
fi

echo "🧠 Ejecutando verificación post-deploy..."
sleep 5
bash ./check_status.sh | tee -a "$LOG_FILE"

echo "✅ Despliegue completado a las $(date)" | tee -a "$LOG_FILE"
