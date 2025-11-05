PROJ ?= asistente-sebastian
REG  ?= us-central1
SVC  ?= natacha-api
URL  ?= https://natacha-api-422255208682.us-central1.run.app

.PHONY: sanity deploy check rollback list logs

sanity:
	bash scripts/traffic_sanity.sh

deploy:
	find . -type f -not -newermt '1980-01-02' -print -exec touch -t 198001020000 {} +
	gcloud run deploy $(SVC) --project $(PROJ) --region $(REG) \
	  --source . --allow-unauthenticated \
	  --revision-suffix="a$$(date +%s)" \
	  --set-env-vars OPENAPI_PUBLIC_URL=$(URL),REV_BUMP="$$(date +%s)"

check:
	@echo "== latestReady / traffic =="
	gcloud run services describe $(SVC) --project $(PROJ) --region $(REG) \
	  --format='value(status.latestReadyRevisionName,status.traffic)'
	@echo "== OpenAPI (/actions /cog) =="
	curl -fsS $(URL)/openapi.v1.json | jq -r '.paths | keys[]' | grep -E '^/(actions|cog)'

list:
	gcloud run revisions list --service $(SVC) --project $(PROJ) --region $(REG) \
	  --format='table(name,trafficPercent,tags.list(),status.conditions[-1].type,status.conditions[-1].status,createTime)'

rollback:
	@rev=$$(gcloud run revisions list --service $(SVC) --project $(PROJ) --region $(REG) \
	  --limit=2 --format='value(name)' | tail -n1); \
	echo "🔙 Rollback a $$rev"; \
	gcloud run services update-traffic $(SVC) --project $(PROJ) --region $(REG) \
	  --to-revisions $$rev=100

logs:
	@rev=$$(gcloud run services describe $(SVC) --project $(PROJ) --region $(REG) \
	  --format='value(status.latestReadyRevisionName)'); \
	echo "== Logs (ERROR) de $$rev =="; \
	gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="$(SVC)" AND resource.labels.revision_name="'$$rev'" AND severity>=ERROR' \
	  --project="$(PROJ)" --freshness=30m --limit=100 --format='value(textPayload)'
