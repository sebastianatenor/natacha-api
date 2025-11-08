.PHONY: guard py sanity
guard:
	bash scripts/guard_no_hardcodes.sh
py:
	python3 -m py_compile $(shell git ls-files '*.py')
sanity: guard py
