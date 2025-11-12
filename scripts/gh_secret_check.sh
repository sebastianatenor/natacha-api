#!/usr/bin/env bash
set -euo pipefail
WF_PATH=".github/workflows/secret-checks-v2.yml"
BRANCH="main"
echo "Dispatching ${WF_PATH} on ${BRANCH}…"
gh workflow run "${WF_PATH}" --ref "${BRANCH}"
echo "Waiting for run id…"
RUN_ID="$(gh run list --workflow "${WF_PATH}" --limit 1 --json databaseId --jq '.[0].databaseId')"
echo "RUN_ID=${RUN_ID}"
gh run watch "${RUN_ID}"
gh run view "${RUN_ID}" --json status,conclusion,displayTitle,jobs \
  --jq '{displayTitle,status,conclusion,jobs:(.jobs|length),names:[.jobs[].name]}'
