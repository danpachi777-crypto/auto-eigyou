#!/usr/bin/env python3
"""Track a kz campaign without starting a background process or sending mail."""

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
STATE = RUNS / "kz-active.json"
LEDGER = ROOT / "ledger.csv"
TARGET = 450


def now():
    return datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(timespec="seconds")


def read_state():
    return json.loads(STATE.read_text()) if STATE.exists() else None


def save_state(state):
    RUNS.mkdir(exist_ok=True)
    temporary = STATE.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(STATE)


def sent_count(campaign_id):
    with LEDGER.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    sent = [row for row in rows if row.get("campaign_id") == campaign_id
            and row.get("delivery_status") == "sent"
            and row.get("gmail_sent_message_id") and row.get("sent_at")]
    ids = [row["gmail_sent_message_id"] for row in sent]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate sent message IDs in this campaign")
    addresses = [row["email"].strip().lower() for row in sent]
    if len(addresses) != len(set(addresses)):
        raise RuntimeError("Duplicate recipients in this campaign")
    return len(ids)


def display(state):
    if not state:
        print("No kz campaign has been started.")
        return
    count = sent_count(state["campaign_id"])
    status = "complete" if count >= TARGET else state["status"]
    print(f"{state['campaign_id']}: {status} — {count}/{TARGET} verified sends")
    if state.get("reason"):
        print(state["reason"])
    if state.get("last_log"):
        print(f"Last log: {state['last_log']}")
    print("Delivery runs only in the Codex conversation after the exact command kz.")
    print(f"State: {STATE}")


def start():
    from storage_guard import reclaim
    reclaim()
    state = read_state()
    if not state or sent_count(state["campaign_id"]) >= TARGET:
        state = {"campaign_id": datetime.now(ZoneInfo("Asia/Tokyo")).strftime("kz-%Y%m%d-%H%M%S"),
                 "status": "ready", "started_at": now(), "reason": ""}
    else:
        state["status"] = "ready"
        state["reason"] = ""
        state.pop("pid", None)
    save_state(state)
    display(state)


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    if command == "start":
        start()
    elif command == "status":
        display(read_state())
    else:
        raise SystemExit("Usage: manual_campaign.py [start|status]")
