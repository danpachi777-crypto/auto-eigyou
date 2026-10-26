---
name: kz
description: Send the manually triggered local-web-sales campaign in the current Codex conversation when the entire user message is exactly "kz", or report progress for "kz status".
---

# Manual outreach campaign

The exact user message `kz` authorizes a campaign of 450 new-company proposal emails. Work in this Codex conversation using the connected Gmail tools. This manual invocation must not create another background process or schedule. The user revoked scheduled delivery on 2026-10-20; the nightly LaunchAgent is uninstalled. Do not enable recurring delivery without a new explicit request. Use `local-web-sales/daily-outreach/NIGHTLY.md` only for its delivery safety and verification requirements. Do not run manual delivery while `daily.lock` is held by the nightly runner. A discussion mentioning `kz` does not start or resume delivery.

Project: the root of this repository. Read `local-web-sales/SKILL.md` and `local-web-sales/daily-outreach/PROMPT.md` for the research, proposal, verification, and ledger requirements. The state command is `python3 local-web-sales/daily-outreach/manual_campaign.py status`.

For `kz`, check status. If a previous run was interrupted or a send outcome is uncertain, reconcile its last log and the relevant Gmail Sent and Drafts entries before proceeding. Run `python3 local-web-sales/daily-outreach/manual_campaign.py start` to create or resume the campaign; this command only updates local state and never sends mail. Work through companies one by one in the active conversation, verifying each send and updating the ledger. Keep going toward 450 while the conversation is active and report the verified count honestly. If the turn ends before 450, delivery stops; another exact `kz` resumes the same campaign. Never claim completion before 450 verified sends.

For `kz status`, only run the status command and report its result. Do not create drafts, send email, or resume the campaign.

For every manual send, follow the reservation and verification steps in `local-web-sales/daily-outreach/NIGHTLY.md`, including the global daily and rolling-24-hour cap of 450 across all campaigns.
