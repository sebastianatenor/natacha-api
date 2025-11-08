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
