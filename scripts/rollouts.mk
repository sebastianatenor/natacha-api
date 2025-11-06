SHELL := /bin/bash
SVC ?= natacha-api
REG ?= us-central1

.PHONY: r.who r.canary r.promote r.rollback

r.who:
	@echo "HASH URL : $$(gcloud run services describe '$(SVC)' --region '$(REG)' --format='value(status.url)')"
	@gcloud run services describe '$(SVC)' --region '$(REG)' \
	  --format='table(status.traffic[].revisionName,status.traffic[].percent)'

# Uso: make r.canary PCT=15
r.canary:
	@set -euo pipefail; \
	PCT="$${PCT:-10}"; SVC='$(SVC)'; REG='$(REG)'; \
	read REV_LATEST REV_PREV < <(gcloud run revisions list --service "$$SVC" --region "$$REG" \
	  --sort-by="~metadata.createTime" --limit=2 --format='value(metadata.name)'); \
	if [[ -z "$$REV_PREV" || "$$REV_LATEST" == "$$REV_PREV" ]]; then \
	  echo "❌ No hay revisión previa para canary (solo $$REV_LATEST). Hacé un deploy para crear otra revisión."; exit 1; \
	fi; \
	echo "Canary $$PCT% -> $$REV_LATEST  |  $$((100-PCT))% -> $$REV_PREV"; \
	gcloud run services update-traffic "$$SVC" --region "$$REG" \
	  --to-revisions "$$REV_LATEST=$$PCT,$$REV_PREV=$$((100-PCT))"

r.promote:
	@set -euo pipefail; \
	SVC='$(SVC)'; REG='$(REG)'; \
	REV_LATEST="$$(gcloud run services describe "$$SVC" --region "$$REG" --format='value(status.latestCreatedRevisionName)')"; \
	echo "Promote 100% -> $$REV_LATEST"; \
	gcloud run services update-traffic "$$SVC" --region "$$REG" --to-revisions "$$REV_LATEST=100"

# Uso: make r.rollback  (o make r.rollback REV=natacha-api-xxxxx)
r.rollback:
	@set -euo pipefail; \
	SVC='$(SVC)'; REG='$(REG)'; \
	REV="$${REV:-$$(gcloud run services describe "$$SVC" --region "$$REG" --format='value(status.traffic[0].revisionName)')}"; \
	if [[ -z "$$REV" ]]; then echo "❌ No pude resolver revisión para rollback"; exit 1; fi; \
	echo "Rollback 100% -> $$REV"; \
	gcloud run services update-traffic "$$SVC" --region "$$REG" --to-revisions "$$REV=100"
