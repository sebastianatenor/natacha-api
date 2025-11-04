#!/usr/bin/env bash
set -euo pipefail

OPENAPI_URL=$(python3 -c "from tools.services import url; print(url('natacha-api','openapi'))")
echo ">> Pulling OpenAPI from: $OPENAPI_URL"
curl -sS "$OPENAPI_URL" -o openapi.json
echo ">> Saved to openapi.json"
