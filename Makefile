SERVICE ?= natacha-memory-console
PROJECT ?= asistente-sebastian
REGION  ?= us-central1
REPO    ?= natacha-repo
IMAGE_NAME ?= memory_console

# URL puede auto-descubrirse con `make url` si querés
URL     ?= https://natacha-memory-console-422255208682.us-central1.run.app

# Si seteás el token, el deploy lo aplica
MEM_CONSOLE_TOKEN ?=

# Versionado automático: v1-YYYYmmdd-HHMMSS-gitsha
GIT_SHA  := $(shell git rev-parse --short HEAD)
STAMP    := $(shell date +%Y%m%d-%H%M%S)
VERSION  ?= v1-$(STAMP)-$(GIT_SHA)

IMG_PATH := $(REGION)-docker.pkg.dev/$(PROJECT)/$(REPO)/$(IMAGE_NAME):$(VERSION)

.PHONY: help build submit deploy roll logs logs-10m logs-errors tail warmup health url describe revisions set-min1

help:
	@echo "Targets:"
	@echo "  make build        - docker build local (etiqueta con VERSION)"
	@echo "  make submit       - gcloud builds submit -> Artifact Registry"
	@echo "  make deploy       - Cloud Run deploy imagen VERSION (aplica MEM_CONSOLE_TOKEN si está)"
	@echo "  make roll         - submit + deploy"
	@echo "  make set-min1     - min instances 1 + cpu boost"
	@echo "  make warmup       - golpea /health 3 veces"
	@echo "  make health       - muestra /health"
	@echo "  make logs         - últimos 30m de logs"
	@echo "  make logs-10m     - últimos 10m de logs"
	@echo "  make logs-errors  - errores de la última hora"
	@echo "  make tail         - tail en vivo de logs"
	@echo "  make url          - URL del servicio"
	@echo "  make describe     - describe del servicio"
	@echo "  make revisions    - lista revisiones"

build:
	@echo ">> Building local image: $(IMG_PATH)"
	docker build -t $(IMG_PATH) memory_console

submit:
	@echo ">> Submitting to Cloud Build -> $(IMG_PATH)"
	gcloud builds submit memory_console \
	  --project=$(PROJECT) \
	  --tag $(IMG_PATH)

deploy:
	@echo ">> Deploying $(SERVICE) with image $(IMG_PATH)"
	@if [ -n "$(strip $(MEM_CONSOLE_TOKEN))" ]; then \
	  echo ">> Applying MEM_CONSOLE_TOKEN env var"; \
	  gcloud run deploy $(SERVICE) \
	    --project=$(PROJECT) \
	    --region=$(REGION) \
	    --image=$(IMG_PATH) \
	    --set-env-vars=MEM_CONSOLE_TOKEN="$(MEM_CONSOLE_TOKEN)" \
	    --allow-unauthenticated; \
	else \
	  gcloud run deploy $(SERVICE) \
	    --project=$(PROJECT) \
	    --region=$(REGION) \
	    --image=$(IMG_PATH) \
	    --allow-unauthenticated; \
	fi
	@$(MAKE) -s warmup

roll: submit deploy

set-min1:
	gcloud run services update $(SERVICE) \
	  --project=$(PROJECT) --region=$(REGION) \
	  --min-instances=1 --cpu-boost

warmup:
	@for i in 1 2 3; do curl -fsS "$(URL)/health" && echo || true; sleep 1; done

health:
	@curl -fsS "$(URL)/health" && echo

logs:
	@gcloud logging read \
	  'resource.type="cloud_run_revision" AND resource.labels.service_name="$(SERVICE)"' \
	  --project=$(PROJECT) --freshness=30m --limit=200 \
	  --format='value(severity, " ", timestamp, " ", textPayload)'

logs-10m:
	@gcloud logging read \
	  'resource.type="cloud_run_revision" AND resource.labels.service_name="$(SERVICE)"' \
	  --project=$(PROJECT) --freshness=10m --limit=200 \
	  --format='value(severity, " ", timestamp, " ", textPayload)'

logs-errors:
	@gcloud logging read \
	  'resource.type="cloud_run_revision" AND resource.labels.service_name="$(SERVICE)" AND severity>=ERROR' \
	  --project=$(PROJECT) --freshness=60m --limit=200 \
	  --format='value(textPayload)'

tail:
	@gcloud beta logging tail \
	  'resource.type="cloud_run_revision" AND resource.labels.service_name="$(SERVICE)"' \
	  --project=$(PROJECT)

url:
	@gcloud run services describe $(SERVICE) \
	  --project=$(PROJECT) --region=$(REGION) \
	  --format='value(status.url)'

describe:
	@gcloud run services describe $(SERVICE) \
	  --project=$(PROJECT) --region=$(REGION)

revisions:
	@gcloud run revisions list \
	  --project=$(PROJECT) --region=$(REGION) \
	  --service=$(SERVICE)

