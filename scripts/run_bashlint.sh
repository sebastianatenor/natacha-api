#!/usr/bin/env bash
set -euo pipefail
shopt -s globstar nullglob

# Juntar todos los .sh del repo por globbing
files=( **/*.sh )

# Filtrar los que NO son zsh (shebang distinto a #!/bin/zsh)
filtered=()
for f in "${files[@]}"; do
  [[ -f "$f" ]] || continue
  if ! head -n1 "$f" | grep -q '^#!/bin/zsh'; then
    filtered+=("$f")
  fi
done

if (( ${#filtered[@]} == 0 )); then
  echo "No bash .sh files"
  exit 0
fi

echo "Bash files:" "${filtered[@]}"

# Sintaxis bash
for f in "${filtered[@]}"; do
  bash -n "$f"
done

# ShellCheck (si está instalado)
if command -v shellcheck >/dev/null 2>&1; then
  shellcheck -S warning "${filtered[@]}"
else
  echo "shellcheck no instalado"
fi

echo "✅ bashlint OK"
