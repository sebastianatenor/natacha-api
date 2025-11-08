. "$(dirname "$0")/../tools/canon_resolver.sh" || source tools/canon_resolver.sh
resolve_canon # exporta CANONICAL
set -euo pipefail

# ====== CONFIGURACIÓN ======
PROJ="asistente-sebastian"
REGION="us-central1"
SERVICE="natacha-api"

# Bucket de backups (se crea si no existe)
BACKUP_BUCKET="gs://asistente-sebastian_backups"

# Carpeta local de backups
BACKUP_DIR="$HOME/backups"
mkdir -p "$BACKUP_DIR"

STAMP="$(date +%Y%m%d-%H%M%S)"
TAG="stable-$STAMP"

echo "==[1/7] Contexto git =="
GIT_HASH="$(git rev-parse --short HEAD || echo 'no-git')"
echo " HEAD: $GIT_HASH"

echo "==[2/7] Tag de git y push de tags =="
git tag -a "$TAG" -m "Stable snapshot $STAMP (limiter hotfix, import_ok:true)"
git push origin --tags || echo "Aviso: no se pudo pushear tags (¿sin remote?)"

echo "==[3/7] ZIP del repo =="
ZIP_PATH="$BACKUP_DIR/natacha-api-$TAG.zip"
zip -r "$ZIP_PATH" . -x ".git/*" ".venv/*" "venv/*" "__pycache__/*" || true
echo " ZIP generado: $ZIP_PATH"

echo "==[4/7] Resolver imagen actual del servicio =="
IMAGE="$(gcloud run services describe "$SERVICE" \
  --project="$PROJ" --region="$REGION" \
  --format='value(spec.template.spec.containers[0].image)')"
if [[ -z "${IMAGE:-}" ]]; then
  echo "ERROR: No pude obtener la imagen del servicio"; exit 1
fi
echo " Imagen actual: $IMAGE"

echo "==[5/7] Etiquetar imagen como :stable =="
gcloud container images add-tag \
  "$IMAGE" \
  "gcr.io/$PROJ/$SERVICE:stable" \
  --quiet --project="$PROJ" || {
    echo "Fallo add-tag; verifico lista de tags por si ya existe…"
  }
echo " Tag :stable aplicado (o ya existente)."

echo "==[6/7] Exportar YAML del servicio =="
YAML_PATH="$BACKUP_DIR/${SERVICE}-service-$TAG.yaml"
gcloud run services describe "$SERVICE" \
  --project="$PROJ" --region="$REGION" \
  --format=yaml > "$YAML_PATH"
echo " YAML exportado: $YAML_PATH"

echo "==[7/7] Subir artefactos al bucket =="
if ! gsutil ls -b "$BACKUP_BUCKET" >/dev/null 2>&1; then
  echo " Bucket no existe, creando $BACKUP_BUCKET…"
  gsutil mb -p "$PROJ" -l "$REGION" "$BACKUP_BUCKET"
fi

DST_PREFIX="$BACKUP_BUCKET/$SERVICE/$STAMP"
gsutil cp "$ZIP_PATH" "$DST_PREFIX/" >/dev/null
gsutil cp "$YAML_PATH" "$DST_PREFIX/" >/dev/null

MANIFEST_PATH="$BACKUP_DIR/${SERVICE}-manifest-$TAG.json"
cat > "$MANIFEST_PATH" <<JSON
{
  "timestamp": "$STAMP",
  "project": "$PROJ",
  "region": "$REGION",
  "service": "$SERVICE",
  "git_head": "$GIT_HASH",
  "git_tag": "$TAG",
  "image_current": "$IMAGE",
  "image_stable": "gcr.io/$PROJ/$SERVICE:stable",
  "zip_local": "$ZIP_PATH",
  "yaml_local": "$YAML_PATH",
  "gcs_prefix": "$DST_PREFIX"
}
JSON

gsutil cp "$MANIFEST_PATH" "$DST_PREFIX/" >/dev/null

echo
echo "================= RESUMEN ================="
echo " Git tag:         $TAG"
echo " Imagen actual:   $IMAGE"
echo " Imagen :stable:  gcr.io/$PROJ/$SERVICE:stable"
echo " ZIP local:       $ZIP_PATH"
echo " YAML local:      $YAML_PATH"
echo " Manifest local:  $MANIFEST_PATH"
echo " GCS destino:     $DST_PREFIX/"
echo "==========================================="
