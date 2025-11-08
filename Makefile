.PHONY: guard py bashlint sanity
guard:
	 bash scripts/guard_no_hardcodes.sh
py:
	 python3 -m py_compile $(shell git ls-files '*.py')
bashlint:
	 bash -lc 'shopt -s globstar nullglob; files=( **/*.sh ); \
	   if [ $${#files[@]} -gt 0 ]; then \
	     for f in "$${files[@]}"; do bash -n "$$f"; done; \
	     command -v shellcheck >/dev/null && shellcheck -S warning "$${files[@]}" || echo "shellcheck no instalado"; \
	   else echo "No .sh files"; fi'
sanity: guard py bashlint
