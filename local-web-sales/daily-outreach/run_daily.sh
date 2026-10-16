#!/bin/zsh
set -euo pipefail

project_root=/Users/kazu/auto-eigyou
workflow_dir="$project_root/local-web-sales/daily-outreach"
run_date=$(/bin/date +%F)
# The user capped 2026-10-16 at the ten drafts already created.
if [[ "$run_date" == 2026-10-16 ]]; then
  exit 0
fi
log_dir="$workflow_dir/runs"
/bin/mkdir -p "$log_dir"

exec /usr/bin/lockf -t 0 "$workflow_dir/daily.lock" \
  /usr/local/bin/codex exec \
    -C "$project_root" \
    --approve-for-me \
    --json \
    - < "$workflow_dir/PROMPT.md" \
    >> "$log_dir/$run_date.jsonl" 2>&1
