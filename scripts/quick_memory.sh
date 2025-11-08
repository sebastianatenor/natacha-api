CANONICAL="${NATACHA_CONTEXT_API:-https://natacha-api-mkwskljrhq-uc.a.run.app}"
#!/usr/bin/env bash
MSG="$1"
[ -z "$MSG" ] && echo "Uso: $0 \"mensaje\"" && exit 1

curl -s -X POST ${CANONICAL}/memory/add \
  -H "Content-Type: application/json" \
  -d "{
    \"summary\": \"$MSG\",
    \"project\": \"LLVC\",
    \"channel\": \"terminal\"
  }" > /dev/null

echo "✅ Memoria enviada: $MSG"
