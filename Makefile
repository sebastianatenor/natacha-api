# ===== Config por defecto (override con env o CLI) =====
SERVICE        ?= natacha-memory-console
PROJECT        ?= asistente-sebastian
REGION         ?= us-central1
REPO           ?= natacha-repo
IMAGE_NAME     ?= memory_console
PCT            ?= 10  # para canary

.PHONY: print-vars warmup check-image deploy deploy-digest promote promote-canary promote-revision rollback status logs

print-vars:
	@echo SERVICE=$(SERVICE)
	@echo PROJECT=$(PROJECT)
	@echo REGION=$(REGION)
	@echo REPO=$(REPO)
	@echo IMAGE_NAME=$(IMAGE_NAME)
	@echo VERSION=$(VERSION)
	@echo DIGEST=$(DIGEST)

warmup:
	@curl -fsS https://$(SERVICE)-422255208682.$(REGION).run.app/health && echo || true

# Verificar imagen por tag
check-image:
	@test -n "$(VERSION)" || (echo "Falta VERSION=vX-YYYYMMDD-..."; exit 1)
	@gcloud artifacts docker images describe \
	  $(REGION)-docker.pkg.dev/$(PROJECT)/$(REPO)/$(IMAGE_NAME):$(VERSION) \
	  --project=$(PROJECT) >/dev/null \
	  && echo "✅ Imagen existe: $(VERSION)"

# Deploy usando tag (VERSION)
deploy: check-image
	@echo ">> Deploying $(SERVICE) with image tag $(VERSION)"
	@gcloud run deploy $(SERVICE) \
	  --project=$(PROJECT) --region=$(REGION) \
	  --image=$(REGION)-docker.pkg.dev/$(PROJECT)/$(REPO)/$(IMAGE_NAME):$(VERSION) \
	  --set-env-vars=MEM_CONSOLE_TOKEN="$(MEM_CONSOLE_TOKEN)" \
	  --allow-unauthenticated
	@$(MAKE) -s warmup

# Deploy usando digest (DIGEST=sha256:...)
deploy-digest:
	@test -n "$(DIGEST)" || (echo "Falta DIGEST=sha256:..."; exit 1)
	@echo ">> Deploying $(SERVICE) with image digest $(DIGEST)"
	@gcloud run deploy $(SERVICE) \
	  --project=$(PROJECT) --region=$(REGION) \
	  --image=$(REGION)-docker.pkg.dev/$(PROJECT)/$(REPO)/$(IMAGE_NAME)@$(DIGEST) \
	  --set-env-vars=MEM_CONSOLE_TOKEN="$(MEM_CONSOLE_TOKEN)" \
	  --allow-unauthenticated
	@$(MAKE) -s warmup

# Mandar 100% a la última revisión lista
promote:
	@gcloud run services update-traffic $(SERVICE) \
	  --project=$(PROJECT) --region=$(REGION) \
	  --to-latest

# Canary: $(PCT)% a la última, resto a estable actual
promote-canary:
	@rev=$$(gcloud run services describe $(SERVICE) --project=$(PROJECT) --region=$(REGION) --format='value(status.latestReadyRevisionName)'); \
	stable=$$(gcloud run services describe $(SERVICE) --project=$(PROJECT) --region=$(REGION) --format='value(status.traffic[0].revisionName)'); \
	echo "Canary $(PCT)% -> $$rev, $$((100-$(PCT)))% -> $$stable"; \
	gcloud run services update-traffic $(SERVICE) \
	  --project=$(PROJECT) --region=$(REGION) \
	  --to-revisions=$$rev=$(PCT),$$stable=$$((100-$(PCT)))

# Promocionar una revisión específica
# Ej: make promote-revision REV=natacha-memory-console-00070-tcp
promote-revision:
	@test -n "$(REV)" || (echo "Falta REV=<revision-name>"; exit 1)
	@gcloud run services update-traffic $(SERVICE) \
	  --project=$(PROJECT) --region=$(REGION) \
	  --to-revisions=$(REV)=100

# Rollback al estable actual (la que hoy tiene tráfico)
rollback:
	@stable=$$(gcloud run services describe $(SERVICE) --project=$(PROJECT) --region=$(REGION) --format='value(status.traffic[0].revisionName)'); \
	echo "Rollback -> $$stable (100%)"; \
	gcloud run services update-traffic $(SERVICE) \
	  --project=$(PROJECT) --region=$(REGION) \
	  --to-revisions=$$stable=100

# Estado rápido
status:
	@gcloud run services describe $(SERVICE) \
	  --project=$(PROJECT) --region=$(REGION) \
	  --format='value(status.traffic[].percent,status.traffic[].revisionName,status.latestReadyRevisionName)'

# Logs últimos 10 minutos
logs:
	@gcloud logs read "run.googleapis.com/service_name=$(SERVICE)" \
	  --project=$(PROJECT) --freshness=10m --limit=100 --format=json \
	  | jq -r '.[].textPayload' || true
