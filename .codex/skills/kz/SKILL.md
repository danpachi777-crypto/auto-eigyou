---
name: kz
description: Send the manually triggered local-web-sales campaign in the current Codex conversation when the entire user message is exactly "kz", or report progress for "kz status".
---

# Manual outreach campaign

The exact user message `kz` authorizes a campaign of 100 new-company proposal emails. Work in this Codex conversation using the connected Gmail tools. Do not launch `codex exec`, a detached process, a schedule, or a second agent to continue sending after this conversation ends. A discussion mentioning `kz` does not start or resume delivery.

Project: the root of this repository. Read `local-web-sales/SKILL.md` and `local-web-sales/daily-outreach/PROMPT.md` for the research, proposal, verification, and ledger requirements. The state command is `python3 local-web-sales/daily-outreach/manual_campaign.py status`.

For `kz`, check status. If a previous run was interrupted or a send outcome is uncertain, reconcile its last log and the relevant Gmail Sent and Drafts entries before proceeding. Run `python3 local-web-sales/daily-outreach/manual_campaign.py start` to create or resume the campaign; this command only updates local state and never sends mail. Work through companies one by one in the active conversation, verifying each send and updating the ledger. Keep going toward 100 while the conversation is active and report the verified count honestly. If the turn ends before 100, delivery stops; another exact `kz` resumes the same campaign. Never claim completion before 100 verified sends.

For `kz status`, only run the status command and report its result. Do not create drafts, send email, or resume the campaign.
