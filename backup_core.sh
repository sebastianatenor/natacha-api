#!/bin/bash
set -e

# 📂 Ir a la carpeta base del proyecto
cd ~/natacha-api

# 🕒 Generar marca de tiempo
DATE=$(date +"%Y%m%d-%H%M")

# 🪣 Verificar o crear bucket de backups
BUCKET="gs://asistente-sebastian-backups"
if ! gsutil ls -b $BUCKET >/dev/null 2>&1; then
  echo "🪣 Bucket no encontrado. Creando $BUCKET ..."
  gsutil mb -l us-central1 $BUCKET
fi

# 🧱 Crear backup (excluyendo archivos .tar.gz previos)
FILE="natacha-core-backup-${DATE}.tar.gz"
tar --exclude='natacha_core/*.tar.gz' -czf "$FILE" natacha_core
echo "✅ Backup creado: $FILE"

# ☁️ Subir a GCS
gsutil cp "$FILE" $BUCKET/
echo "☁️  Subido a GCS: $BUCKET/$FILE"

# 🧹 Limpiar backups antiguos (mantiene los 5 más recientes)
echo "🧹 Limpiando backups antiguos (manteniendo los 5 más recientes)..."
TOTAL=$(gsutil ls -l $BUCKET | grep "natacha-core-backup" | wc -l)
if [ "$TOTAL" -gt 5 ]; then
  REMOVE=$((TOTAL - 5))
  echo "🧹 Eliminando $REMOVE backups antiguos..."
  gsutil ls -l $BUCKET | grep "natacha-core-backup" | sort -k2 | head -n $REMOVE | awk '{print $3}' | xargs -I {} gsutil rm {}
else
  echo "ℹ️ No hay backups antiguos para eliminar."
fi

echo "✅ Todo listo."
