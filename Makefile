SHELL := /usr/bin/env bash

.PHONY: guard py bashlint sanity

guard:
	@bash scripts/guard_no_hardcodes.sh

py:
	@python3 -m py_compile $(shell git ls-files '*.py')

bashlint:
	@bash scripts/run_bashlint.sh

sanity: guard py bashlint

.PHONY: health
health:
	@bash scripts/health_probe.sh

.PHONY: memory-smoke
memory-smoke:
	@echo Storing sample... && curl -s -X POST "$${CANON:-http://127.0.0.1:8080}/memory/v2/store" -H "Content-Type: application/json" -d '{"items":[{"text":"Client Nubicom asks for CAT 320D","tags":["lead","excavator"]},{"text":"Aguas del Norte prefers proforma before VIN","tags":["lead","invoice"]}]}' | jq . && \
	echo Searching... && curl -s -X POST "$${CANON:-http://127.0.0.1:8080}/memory/v2/search" -H "Content-Type: application/json" -d '{"query":"proforma VIN","top_k":5,"use_semantic":true}' | jq .

.PHONY: deploy
deploy:
	gcloud run deploy natacha-api --region us-central1 --source . --set-secrets API_KEY=NATACHA_API_KEY:latest

.PHONY: memory-smoke-remote
memory-smoke-remote:
	@export CANON=$$(gcloud run services describe natacha-api --region us-central1 --format="value(status.url)"); \
	KEY=$$(gcloud secrets versions access latest --secret NATACHA_API_KEY --project asistente-sebastian | tr -d '\r\n'); \
	printf "Store...\n"; \
	curl -s -X POST "$$CANON/memory/v2/store" \
	  -H "Content-Type: application/json" -H "X-API-Key: $$KEY" \
	  -d '{"items":[{"text":"Smoke item","tags":["smoke"]}]}' | jq .; \
	printf "Search...\n"; \
	curl -s -X POST "$$CANON/memory/v2/search" \
	  -H "Content-Type: application/json" -H "X-API-Key: $$KEY" \
	  -d '{"query":"Smoke","top_k":3}' | jq .

.PHONY: deploy-gcs
deploy-gcs:
	gcloud run deploy natacha-api --region us-central1 --source . \
	  --set-secrets API_KEY=NATACHA_API_KEY:latest \
	  --set-env-vars MEMORY_FILE=gs://natacha-memory-store/memory_store.jsonl,RATE_LIMIT_DISABLE=1

.PHONY: memory-check
memory-check:
	@CANON=$$(gcloud run services describe natacha-api --region us-central1 --format='value(status.url)'); \
	KEY=$$(gcloud secrets versions access latest --secret NATACHA_API_KEY --project asistente-sebastian | tr -d '\r\n'); \
	echo "info:"; \
	curl -s -H "X-API-Key: $$KEY" "$$CANON/memory/v2/ops/memory-info" | jq . || true; \
	echo "store:"; \
	curl -s -X POST "$$CANON/memory/v2/store" -H "Content-Type: application/json" -H "X-API-Key: $$KEY" \
	     -d '{"items":[{"text":"consistency-check","tags":["probe","ci"]}]}' | jq .; \
	echo "search:"; \
	curl -s -X POST "$$CANON/memory/v2/search" -H "Content-Type: application/json" -H "X-API-Key: $$KEY" \
	     -d '{"query":"consistency","top_k":3}' | jq .

.PHONY: compact-now
compact-now:
	@gcloud run jobs execute natacha-compact --region us-central1 --wait

.PHONY: deploy-prod
deploy-prod:
	@gcloud run deploy natacha-api --region us-central1 --source . \
	  --set-secrets API_KEY=NATACHA_API_KEY:latest \
	  --env-vars-file env.prod

.PHONY: deploy-prod
deploy-prod:
	@gcloud run deploy natacha-api --region us-central1 --source . \
	  --set-secrets API_KEY=NATACHA_API_KEY:latest \
	  --env-vars-file env.prod.yaml
health-memory:
	BASE=${BASE:-http://localhost:8080} scripts/health_memory.sh
.PHONY: health-memory
health-all: health-memory health-tasks health-ops
	@echo "✅ All subsystems healthy"
.PHONY: health-all
health-tasks:
	BASE=${BASE:-http://localhost:8080} scripts/health_tasks.sh
.PHONY: health-tasks

health-ops:
	BASE=${BASE:-http://localhost:8080} scripts/health_ops.sh
.PHONY: health-ops

health-all: health-memory health-tasks health-ops
	@echo "✅ All subsystems healthy"
.PHONY: health-all
