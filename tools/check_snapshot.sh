#!/usr/bin/env bash
set -euo pipefail

S="$(ls -1dt "$HOME/Projects/natacha-api/infra_snapshots"/20*Z | head -n1)"
echo "Latest snapshot: $S"
ls -lah "$S"

echo
echo "== Quick counts =="
# these files may not exist if a section failed; guard with || echo
jq 'length' "$S/run.services.out" 2>/dev/null || echo "n/d (run.services)"
jq 'length' "$S/sched.jobs.out"   2>/dev/null || echo "n/d (sched.jobs)"
jq 'length' "$S/mon.policies.out" 2/ dev/null || echo "n/d (mon.policies)"

echo
echo "== First 5 Cloud Run services =="
if [ -s "$S/run.services.out" ]; then
  # IMPORTANT: do NOT backslash-escape quotes inside the single-quoted jq program
  jq -r '.[0:5][] | "- \(.metadata.name) -> \(.status.url // "s/n")"' "$S/run.services.out"
else
  echo "_no data_"
fi

echo
echo "== First 5 Scheduler jobs =="
if [ -s "$S/sched.jobs.out" ]; then
  jq -r '.[0:5][] | "- \(.name | split("/")[ -1]) @ \(.schedule) [\(.state)]"' "$S/sched.jobs.out"
else
  echo "_no data_"
fi

echo
echo "== IAM (roles/run.invoker) =="
if [ -s "$S/iam.run_invokers.out" ]; then
  sed 's/^/  /' "$S/iam.run_invokers.out" | sed -e '1,1s/^/  (role, member)\n/'
else
  echo "_no data_"
fi
