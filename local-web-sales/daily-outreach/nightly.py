#!/usr/bin/env python3
"""Run bounded, serial Codex outreach jobs overnight with an exclusive lock."""

import argparse
import fcntl
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from delivery_budget import LIMIT, connect, status

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
RUNS = ROOT / "runs"
CODEX = Path.home() / ".local" / "bin" / "codex"


def night_window(now):
    """Skip delayed daytime launches; all work ends by 09:00 Japan time."""
    if 9 <= now.hour < 21:
        return None
    night = now if now.hour >= 21 else now - timedelta(days=1)
    end = (night + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    return night.strftime("nightly-%Y%m%d"), end


def command(output):
    return [str(CODEX), "-a", "never", "-s", "workspace-write", "--search", "exec",
            "-C", str(PROJECT), "--json", "-o", str(output), "-"]


def preflight():
    """Exercise the scheduled CLI's real read-only connector access, never delivery."""
    RUNS.mkdir(exist_ok=True)
    output = RUNS / "preflight-result.txt"
    prompt = (
        "Read-only nightly outreach preflight. DO NOT send emails, create/update drafts, "
        "generate images, alter any files or settings, or start a campaign. "
        "Discover available tool metadata for Gmail profile, search, read, draft, send and "
        "built-in ImageGen; do not invoke write tools. Read the connected Gmail profile. "
        "Return JSON with gmail_account, gmail_read_ok, gmail_draft_tool_available, "
        "gmail_send_tool_available, imagegen_tool_available, web_search_available, and blockers. "
        "Do not infer availability from local skill text. If a tool cannot be discovered, "
        "mark it unavailable. The required Gmail account is danpachi777@gmail.com."
    )
    with (RUNS / "preflight-events.jsonl").open("w") as log:
        process = subprocess.Popen(command(output), cwd=PROJECT, stdin=subprocess.PIPE,
                                   stdout=log, stderr=log, text=True, start_new_session=True)
        try:
            process.communicate(prompt, timeout=120)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            print("Read-only preflight timed out; delivery readiness is unverified.")
            return 1
    return finish_preflight(process.returncode)


def finish_preflight(returncode):
    """Require a successful actual Gmail read as well as discovered write tools."""
    output = RUNS / "preflight-result.txt"
    if output.exists():
        print(output.read_text())
    try:
        result = json.loads(output.read_text())
        required = ("gmail_read_ok", "gmail_draft_tool_available", "gmail_send_tool_available",
                    "imagegen_tool_available", "web_search_available")
        profile_verified = False
        for line in (RUNS / "preflight-events.jsonl").read_text().splitlines():
            event = json.loads(line)
            item = event.get("item", {})
            if (event.get("type") == "item.completed" and item.get("tool") == "gmail.get_profile"
                    and item.get("status") == "completed"):
                profile = (item.get("result") or {}).get("structured_content", {})
                profile_verified = profile.get("email") == "danpachi777@gmail.com"
        ready = (returncode == 0 and profile_verified and not result.get("blockers")
                 and result.get("gmail_account") == "danpachi777@gmail.com"
                 and all(result.get(field) is True for field in required))
        (RUNS / "preflight.json").write_text(json.dumps({
            "ready": ready, "checked_at": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(),
            "result": result}, ensure_ascii=False, indent=2) + "\n")
        return 0 if ready else 1
    except (OSError, ValueError, TypeError):
        print("Could not verify nightly tool readiness.")
        return 1


def run(dry_run=False):
    RUNS.mkdir(exist_ok=True)
    if dry_run:
        print(json.dumps({"schedule": "21:00 Asia/Tokyo daily", "limit": LIMIT,
                          "command": command(RUNS / "last-message.txt"),
                          "prompt": str(ROOT / "NIGHTLY.md"), "sends_mail": False}, ensure_ascii=False))
        return 0
    lock = (ROOT / "daily.lock").open("a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("An outreach run is already active; skipping.")
        return 0
    started = datetime.now(ZoneInfo("Asia/Tokyo"))
    window = night_window(started)
    if window is None:
        print("Outside the 21:00-09:00 Japan night window; no delivery started.")
        lock.close()
        return 0
    campaign, ends_at = window
    folder = RUNS / started.strftime("%Y%m%d-%H%M%S-%f")
    folder.mkdir()
    report = {"campaign_id": campaign, "started_at": started.isoformat(),
              "limit": LIMIT, "status": "running", "iterations": 0}
    report_path = folder / "report.json"

    def save():
        report["updated_at"] = datetime.now(ZoneInfo("Asia/Tokyo")).isoformat()
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")

    save()
    deadline = time.monotonic() + (ends_at - started).total_seconds()
    try:
        for number in range(1, LIMIT + 1):
            with connect() as database:
                before = status(database)
            report["budget"] = before
            if before["pending"] or before["remaining"] == 0:
                report["status"] = "pending_reconciliation" if before["pending"] else "limit_reached"
                break
            if time.monotonic() >= deadline:
                report["status"] = "night_window_ended"
                break
            output = folder / f"{number:03d}-result.txt"
            with connect() as database:
                confirmed_before = database.execute(
                    "SELECT COUNT(*) FROM deliveries WHERE campaign=? AND status='sent'", (campaign,)).fetchone()[0]
            prompt = (ROOT / "NIGHTLY.md").read_text()
            prompt += f"\nCampaign ID: {campaign}\nIteration: {number}\n"
            with (folder / f"{number:03d}-events.jsonl").open("w") as log:
                process = subprocess.Popen(command(output), cwd=PROJECT, stdin=subprocess.PIPE,
                                           stdout=log, stderr=log, text=True, start_new_session=True)
                try:
                    process.communicate(prompt, timeout=min(1800, max(1, deadline - time.monotonic())))
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                    report["status"] = "timeout_reconcile_before_retry"
                    break
            report["iterations"] = number
            with connect() as database:
                after = status(database)
            report["budget"] = after
            if process.returncode:
                report["status"] = "codex_error"
                report["returncode"] = process.returncode
                break
            if after["pending"]:
                report["status"] = "pending_reconciliation"
                break
            # A job must confirm exactly one delivery, not merely claim success.
            with connect() as database:
                confirmed = database.execute(
                    "SELECT COUNT(*) FROM deliveries WHERE campaign=? AND status='sent'", (campaign,)).fetchone()[0]
            if confirmed != confirmed_before + 1:
                report["status"] = "no_verified_delivery"
                break
            report["confirmed_campaign"] = confirmed
            save()
        else:
            report["status"] = "iteration_limit_reached"
    except Exception as error:
        report["status"] = "error"
        report["error"] = str(error)
    finally:
        save()
        print(json.dumps(report, ensure_ascii=False))
        lock.close()
    return 0 if report["status"] in ("limit_reached", "iteration_limit_reached", "night_window_ended") else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    sys.exit(preflight() if args.preflight else run(args.dry_run))
