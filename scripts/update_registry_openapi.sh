. "$(dirname "$0")/../tools/canon_resolver.sh" || source tools/canon_resolver.sh
resolve_canon # exporta CANONICAL
#!/usr/bin/env bash
set -euo pipefail

SERVICE="natacha-api"
PROJECT_ID="asistente-sebastian"
REGION="us-central1"
GOOD_URL="${CANONICAL}"

REV="$(gcloud run services describe "$SERVICE" --project="$PROJECT_ID" --region="$REGION" --format='value(status.latestReadyRevisionName)')"

# Eliminar bloques previos del OpenAPI en REGISTRY.md
perl -0777 -pe 's/\n*---\n+### (?:\xF0\x9F\xA7\xA9|<0001f9e9>) OpenAPI Schema .*?(?=\n---\n|\Z)//gms' -i REGISTRY.md 2>/dev/null || true
# Compactar separadores/líneas en blanco
perl -0777 -pe 's/\n{3,}/\n\n/g; s/(?:\n---\n){2,}/\n---\n/g' -i REGISTRY.md 2>/dev/null || true

cat >> REGISTRY.md <<EOF

---

### <0001f9e9> OpenAPI Schema (Cloud Run / Natacha API)

**Servicio:** \`$SERVICE\`
**Proyecto:** \`$PROJECT_ID\`
**Región:** \`$REGION\`
**Revisión activa:** \`$REV\`
**URL público:** [$GOOD_URL]($GOOD_URL)

#### 📘 Endpoint de esquema (para Actions / herramientas externas)
- JSON: \`$GOOD_URL/openapi.v1.json\`

#### <0001f9f1> Estructura técnica
- **Base module serving:** \`entrypoint_app.py\`
- **Router responsable:** \`routes/openapi_compat.py\`
- **Versión de OpenAPI publicada:** \`3.1.0\`
- **Servers:** \`[{ "url": "$GOOD_URL" }]\`
- **Env var usada:** \`OPENAPI_PUBLIC_URL\`
- **Propósito:** Publicar un esquema OpenAPI compatible con Actions y otras integraciones externas.

#### 🛠 Cómo actualizar solo la versión del esquema
1. Editar \`routes/openapi_compat.py\` y ajustar: \`schema["openapi"] = "3.1.0"\` (o \`"3.1.1"\` si tu editor lo exige).
2. Build & deploy normales del servicio.
3. Verificar: \`curl -fsS "$GOOD_URL/openapi.v1.json" | jq '.openapi, .servers'\`
EOF

echo "✅ REGISTRY.md actualizado."
echo "🔎 Servers actuales:"; curl -fsS "$GOOD_URL/openapi.v1.json" | jq '.servers'
