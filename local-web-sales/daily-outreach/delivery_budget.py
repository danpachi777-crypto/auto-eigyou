#!/usr/bin/env python3
"""Reserve one delivery slot before Gmail sending; never send mail here."""

import argparse
import csv
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
DB = ROOT / "runs" / "delivery-budget.sqlite3"
LEDGER = ROOT / "ledger.csv"
FAILED_RECIPIENTS = ROOT / "failed-recipients.csv"
LIMIT = 450
TZ = ZoneInfo("Asia/Tokyo")


def clock():
    return datetime.now(TZ)


def connect(path=DB):
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30, isolation_level=None)
    connection.execute("""CREATE TABLE IF NOT EXISTS deliveries (
        email TEXT PRIMARY KEY, company TEXT NOT NULL, campaign TEXT NOT NULL,
        reserved_at TEXT NOT NULL, status TEXT NOT NULL,
        message_id TEXT UNIQUE, sent_at TEXT)""")
    return connection


def historical(now, ledger=LEDGER):
    with ledger.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    addresses, recent, today = set(), set(), set()
    for row in rows:
        email = row["email"].strip().casefold()
        addresses.add(email)
        if row["delivery_status"] not in ("sent", "sent_by_user"):
            if row["delivery_status"] in ("sending", "uncertain"):
                raise ValueError("Reconcile an uncertain ledger delivery before resuming")
            continue
        if row.get("sent_at"):
            stamp = datetime.fromisoformat(row["sent_at"])
            if stamp.tzinfo is None:
                raise ValueError("A ledger sent_at value lacks a timezone")
            stamp = stamp.astimezone(TZ)
            if stamp > now:
                raise ValueError("A ledger delivery timestamp is in the future")
            if stamp > now - timedelta(hours=24):
                recent.add(email)
            if stamp.date() == now.date():
                today.add(email)
        else:
            # Old user-confirmed sends lack exact times. Count yesterday and today
            # conservatively until the end of the following calendar day.
            date = datetime.fromisoformat(row["run_date"]).date()
            if date >= (now - timedelta(hours=24)).date():
                recent.add(email)
            if date >= now.date():
                today.add(email)
    return addresses, recent, today


def status(connection, now=None, ledger=LEDGER):
    now = now or clock()
    _, recent, today = historical(now, ledger)
    pending = []
    for email, reserved, state, sent_at in connection.execute(
            "SELECT email, reserved_at, status, sent_at FROM deliveries"):
        stamp = datetime.fromisoformat(sent_at or reserved).astimezone(TZ)
        if state == "pending":
            pending.append(email)
        if stamp > now - timedelta(hours=24):
            recent.add(email)
        if stamp.date() == now.date():
            today.add(email)
    return {"limit": LIMIT, "sent_or_reserved_today": len(today),
            "sent_or_reserved_24h": len(recent), "pending": pending,
            "remaining": 0 if pending else max(0, LIMIT - max(len(today), len(recent)))}


def reserve(connection, email, company, campaign, gmail_count, now=None, ledger=LEDGER):
    now = now or clock()
    email = email.strip().casefold()
    if "@" not in email or gmail_count < 0:
        raise ValueError("Invalid email or Gmail 24-hour count")
    if FAILED_RECIPIENTS.exists():
        with FAILED_RECIPIENTS.open(newline="", encoding="utf-8-sig") as stream:
            failed = {row["email"].strip().casefold() for row in csv.DictReader(stream)}
        if email in failed:
            raise ValueError("Recipient has a confirmed delivery failure; choose another company")
    connection.execute("BEGIN IMMEDIATE")
    try:
        known, _, _ = historical(now, ledger)
        budget = status(connection, now, ledger)
        if email in known:
            raise ValueError("Recipient already exists in the ledger; do not resend")
        if budget["pending"]:
            raise ValueError("Reconcile the pending delivery with Gmail before sending")
        if budget["remaining"] < 1 or gmail_count >= LIMIT:
            raise ValueError("Daily or rolling 24-hour delivery limit reached")
        connection.execute("INSERT INTO deliveries VALUES (?, ?, ?, ?, 'pending', NULL, NULL)",
                           (email, company, campaign, now.isoformat()))
        connection.execute("COMMIT")
    except Exception:
        connection.execute("ROLLBACK")
        raise


def confirm(connection, email, message_id, sent_at):
    stamp = datetime.fromisoformat(sent_at)
    if not message_id.strip() or stamp.tzinfo is None or stamp > clock():
        raise ValueError("A verified Gmail message ID and timezone-aware sent time are required")
    row = connection.execute("SELECT reserved_at FROM deliveries WHERE email=? AND status='pending'",
                             (email.strip().casefold(),)).fetchone()
    if row is None or stamp < datetime.fromisoformat(row[0]):
        raise ValueError("Sent time must belong to the pending reservation")
    result = connection.execute(
        "UPDATE deliveries SET status='sent', message_id=?, sent_at=? WHERE email=? AND status='pending'",
        (message_id, stamp.isoformat(), email.strip().casefold()))
    if result.rowcount != 1:
        raise ValueError("No pending reservation for this email")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    pending = sub.add_parser("reserve")
    for field in ("email", "company", "campaign"):
        pending.add_argument("--" + field, required=True)
    pending.add_argument("--gmail-count", type=int, required=True,
                         help="Fully paginated count of all connected-account Sent messages in the last 24h")
    done = sub.add_parser("confirm")
    for field in ("email", "message-id", "sent-at"):
        done.add_argument("--" + field, required=True)
    args = parser.parse_args()
    with connect() as connection:
        if args.command == "reserve":
            reserve(connection, args.email, args.company, args.campaign, args.gmail_count)
        elif args.command == "confirm":
            confirm(connection, args.email, args.message_id, args.sent_at)
        print(json.dumps(status(connection), ensure_ascii=False))


if __name__ == "__main__":
    main()
