---
name: kz
description: Run the manually triggered local-web-sales campaign when the user enters the exact command "kz" in Codex, or inspect it with "kz status".
---

# Manual outreach campaign

The exact user message `kz` authorizes one campaign of 100 new-company proposal emails. Never start a campaign from a schedule, from mentioning this skill in discussion, or from `kz status`.

Project: `/Users/kazu/auto-eigyou`. Read the `local-web-sales` skill for content and verification requirements. The campaign runner is `local-web-sales/daily-outreach/manual_campaign.py`. It runs Codex in batches of at most five, counts only campaign-tagged ledger rows with sent message IDs and timestamps, and keeps working in the background until 100 are verified or a blocker is recorded. Do not launch a second runner for the same active campaign.

For `kz`, check `python3 local-web-sales/daily-outreach/manual_campaign.py status`. If a previous campaign is blocked, inspect its last JSONL log and reconcile uncertain Gmail sends against Sent and Drafts before resuming. Then run `python3 local-web-sales/daily-outreach/manual_campaign.py start`. This command resumes an incomplete campaign; after a completed campaign it starts a new one. Tell the user the campaign ID, current count, and that work is running in the background. Check status again before claiming completion. Only claim 100 when the runner reports `complete` and 100/100.

For `kz status`, only run the status command and report its result. If blocked, report the exact reason and log path. A blocked campaign needs diagnosis and a safe resume; do not invent a completion or send a duplicate.
