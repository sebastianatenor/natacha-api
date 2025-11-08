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
