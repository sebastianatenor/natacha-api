#!/bin/bash
set -e

echo "🚀 Iniciando entorno local de Natacha..."
echo "──────────────────────────────────────────"

PROJECT_ID="asistente-sebastian"
CREDENTIALS_PATH="$HOME/.config/gcloud/application_default_credentials.json"
IMAGE_NAME="natacha-brain-local"

# 1️⃣ Validar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
  echo "❌ No se encontró 'gcloud'. Instalalo desde https://cloud.google.com/sdk/docs/install"
  exit 1
fi

# 2️⃣ Verificar login de usuario
ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
if [ -z "$ACTIVE_ACCOUNT" ]; then
  echo "⚠️ No hay usuario autenticado. Ejecutá:"
  echo "   gcloud auth login"
  exit 1
else
  echo "✅ Usuario autenticado: $ACTIVE_ACCOUNT"
fi

# 3️⃣ Verificar proyecto
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || true)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
  echo "⚠️ Proyecto incorrecto (actual: $CURRENT_PROJECT)"
  echo "   Configurando proyecto a $PROJECT_ID ..."
  gcloud config set project "$PROJECT_ID" >/dev/null
fi
echo "✅ Proyecto activo: $PROJECT_ID"

# 4️⃣ Verificar credenciales de aplicación
if [ ! -f "$CREDENTIALS_PATH" ]; then
  echo "⚠️ No se encontraron credenciales de aplicación."
  echo "   Ejecutá: gcloud auth application-default login"
  exit 1
else
  echo "✅ Credenciales ADC disponibles."
fi

# 5️⃣ Verificar imagen Docker local
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
  echo "⚠️ No se encontró la imagen local '$IMAGE_NAME'."
  echo "   Ejecutá: docker build -t $IMAGE_NAME ."
  exit 1
else
  echo "✅ Imagen Docker: $IMAGE_NAME"
fi

# 6️⃣ Ejecutar el contenedor
echo "──────────────────────────────────────────"
echo "🏁 Iniciando contenedor local en http://localhost:8080 ..."
echo "──────────────────────────────────────────"

docker run -p 8080:8080 \
  -v "$CREDENTIALS_PATH":/root/.config/gcloud/application_default_credentials.json \
  -e GOOGLE_CLOUD_PROJECT="$PROJECT_ID" \
  "$IMAGE_NAME"
