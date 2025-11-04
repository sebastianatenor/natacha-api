#!/usr/bin/env bash
set -e
URL="https://natacha-api-422255208682.us-central1.run.app/openapi.json"
DEST="/tmp/natacha-openapi.json"

echo "📥 Bajando OpenAPI desde $URL ..."
curl -s "$URL" | python3 -m json.tool > "$DEST"
echo "✅ Listo: $DEST"
echo "👉 Ahora abrilo y pegalo en el Builder."
