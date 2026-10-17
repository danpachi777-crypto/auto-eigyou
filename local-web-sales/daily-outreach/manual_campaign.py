#!/usr/bin/env python3
"""Start, resume, and monitor a manually triggered 100-send Codex campaign."""

import csv
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent.parent
RUNS = ROOT / "runs"
STATE = RUNS / "kz-active.json"
LOCK = RUNS / "kz.lock"
LEDGER = ROOT / "ledger.csv"
PROMPT = ROOT / "PROMPT.md"
TARGET = 100
BATCH = 5
CODEX = shutil.which("codex") or "/usr/local/bin/codex"


def now():
    return datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(timespec="seconds")


def read_state():
    return json.loads(STATE.read_text()) if STATE.exists() else None


def save_state(state):
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
    print(f"{state['campaign_id']}: {state['status']} — {count}/{TARGET} verified sends")
    if state.get("reason"):
        print(state["reason"])
    print(f"State: {STATE}")


def start():
    RUNS.mkdir(exist_ok=True)
    state = read_state()
    if state and state["status"] == "running":
        pid = state.get("pid")
        if pid:
            try:
                os.kill(pid, 0)
                display(state)
                return
            except ProcessLookupError:
                pass
    if not state or state["status"] == "complete":
        state = {"campaign_id": datetime.now(ZoneInfo("Asia/Tokyo")).strftime("kz-%Y%m%d-%H%M%S"),
                 "status": "running", "started_at": now(), "round": 0, "reason": ""}
    else:
        state["status"] = "running"
        state["reason"] = ""
    state["pid"] = None
    save_state(state)
    with (RUNS / "kz-supervisor.log").open("ab") as log:
        process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "run"],
                                   cwd=PROJECT, stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=subprocess.STDOUT,
                                   start_new_session=True)
    state["pid"] = process.pid
    save_state(state)
    display(state)


def run():
    with LOCK.open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        for _ in range(100):
            state = read_state()
            if state and state.get("pid") == os.getpid():
                break
            time.sleep(0.01)
        else:
            return
        if not state or state["status"] != "running":
            return
        try:
            while True:
                before = sent_count(state["campaign_id"])
                if before >= TARGET:
                    state.update(status="complete", completed_at=now(), reason="")
                    break
                limit = min(BATCH, TARGET - before)
                state["round"] += 1
                state["last_round_at"] = now()
                save_state(state)
                instruction = (f"Campaign ID: {state['campaign_id']}\n"
                               f"This execution must send and verify exactly {limit} NEW companies "
                               f"for this campaign. Already verified: {before}/{TARGET}. "
                               f"Stop at {limit}; the runner handles subsequent batches.\n\n"
                               + PROMPT.read_text())
                log_path = RUNS / f"{state['campaign_id']}-round-{state['round']:03}.jsonl"
                with log_path.open("wb") as log:
                    result = subprocess.run([CODEX, "exec", "-C", str(PROJECT),
                                             "--approve-for-me", "--json", "-"],
                                            input=instruction.encode(), stdout=log,
                                            stderr=subprocess.STDOUT, cwd=PROJECT)
                after = sent_count(state["campaign_id"])
                state["verified_sends"] = after
                state["last_log"] = str(log_path)
                if after > TARGET or after - before > limit:
                    raise RuntimeError("Batch exceeded its send limit; inspect Gmail and ledger")
                if result.returncode or after == before:
                    state.update(status="blocked", reason=(
                        f"Round {state['round']} ended with exit {result.returncode}; "
                        f"verified progress {before} → {after}. Inspect {log_path}"))
                    break
                save_state(state)
        except Exception as error:
            state.update(status="blocked", reason=f"Supervisor error: {error}")
        finally:
            save_state(state)


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    if command == "start":
        start()
    elif command == "run":
        run()
    elif command == "status":
        display(read_state())
    else:
        raise SystemExit("Usage: manual_campaign.py [start|status]")
