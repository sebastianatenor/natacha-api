#!/usr/bin/env bash
MSG="$1"
[ -z "$MSG" ] && echo "Uso: $0 \"mensaje\"" && exit 1

curl -s -X POST https://natacha-api-422255208682.us-central1.run.app/memory/add \
  -H "Content-Type: application/json" \
  -d "{
    \"summary\": \"$MSG\",
    \"project\": \"LLVC\",
    \"channel\": \"terminal\"
  }" > /dev/null

echo "✅ Memoria enviada: $MSG"
