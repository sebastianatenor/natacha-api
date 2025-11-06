SHELL := /bin/bash
SVC ?= natacha-api
REG ?= us-central1
PROJ ?= $(shell gcloud config get-value project)
PROJNUM := $(shell gcloud projects describe $(PROJ) --format='value(projectNumber)')
URL_CANON := https://$(SVC)-$(PROJNUM).$(REG).run.app
.PHONY: print url url-hash svcinfo deploy set-canon smoke hard-smoke logs to-latest promote traffic rollback
print:
url-hash:
url:
svcinfo:
deploy:
set-canon:
smoke:
hard-smoke:
logs:
to-latest:
promote: to-latest svcinfo
traffic:
verify:
# --- Rollouts cómodos ---
.PHONY: who canary promote rollback
who:
# Uso: make canary SVC=natacha-api REG=us-central1 PCT=10
canary:
# Uso: make promote SVC=natacha-api REG=us-central1
promote:
# Uso: make rollback SVC=natacha-api REG=us-central1 [REV=natacha-api-xxxxx]
include scripts/rollouts.mk
