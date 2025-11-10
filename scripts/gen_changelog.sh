#!/usr/bin/env bash
set -euo pipefail
usage(){ echo "Uso: $0 --current <TAG> [--previous <TAG_PREV>] [--repo <URL>] [--outfile <PATH>]"; exit 1; }
CUR="" PREV="" REPO="" OUT=""
while [[ $# -gt 0 ]]; do case "$1" in
  --current) CUR="${2:-}"; shift 2;;
  --previous) PREV="${2:-}"; shift 2;;
  --repo) REPO="${2:-}"; shift 2;;
  --outfile) OUT="${2:-}"; shift 2;;
  *) usage;;
esac; done
[[ -n "$CUR" ]] || usage
if [[ -z "$REPO" ]]; then
  origin="$(git remote get-url origin)"
  if [[ "$origin" =~ ^git@github\.com:(.*)\.git$ ]]; then REPO="https://github.com/${BASH_REMATCH[1]}";
  elif [[ "$origin" =~ ^https?:// ]]; then REPO="${origin%.git}"; else echo "No se pudo resolver URL del repo"; exit 1; fi
fi
[[ -n "$PREV" ]] || PREV="$(git tag --list 'stable-*' --sort=-v:refname | sed -n '2p' || true)"
RANGE="$CUR"; TITLE="## ${CUR} – $(date -u +%Y-%m-%d) (UTC)"
[[ -n "$PREV" ]] && RANGE="${PREV}..${CUR}"
COMPARE_LINE=$([[ -n "$PREV" ]] && echo "**Diff:** ${REPO}/compare/${PREV}...${CUR}" || echo "**Inicio:** ${CUR} (sin tag previo)")
COMMITS="$(git log --no-merges --pretty='- %s (%h) — %an' ${RANGE} || true)"
feat="$(git log --no-merges --grep='^feat'  --pretty='- %s (%h) — %an' ${RANGE} || true)"
fixs="$(git log --no-merges --grep='^fix'   --pretty='- %s (%h) — %an' ${RANGE} || true)"
chore="$(git log --no-merges --grep='^chore' --pretty='- %s (%h) — %an' ${RANGE} || true)"
docs="$(git log --no-merges --grep='^docs'  --pretty='- %s (%h) — %an' ${RANGE} || true)"
{
  echo "$TITLE"; echo; echo "$COMPARE_LINE"; echo;
  [[ -n "$feat"  ]] && { echo "### Features"; echo "$feat"; echo; }
  [[ -n "$fixs"  ]] && { echo "### Fixes"; echo "$fixs"; echo; }
  [[ -n "$docs"  ]] && { echo "### Docs"; echo "$docs"; echo; }
  [[ -n "$chore" ]] && { echo "### Chores"; echo "$chore"; echo; }
  echo "### Commits"; [[ -n "$COMMITS" ]] && echo "$COMMITS" || echo "- (sin cambios)"
  echo
} | { [[ -n "$OUT" ]] && tee "$OUT" || cat; }
