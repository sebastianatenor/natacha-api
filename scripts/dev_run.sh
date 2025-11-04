#!/usr/bin/env bash
set -e
export NATACHA_REMOTE_BOOTSTRAP=0
export REMOTE_BASE_URL="https://natacha-api-422255208682.us-central1.run.app"
python -m uvicorn natacha_app:app --host 0.0.0.0 --port 8081 --reload
