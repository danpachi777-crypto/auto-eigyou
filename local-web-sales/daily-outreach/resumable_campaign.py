#!/usr/bin/env python3
"""One requested campaign, with durable progress and offline waiting; no scheduler.

The default invocation is read-only. --run starts sequential Codex jobs and needs explicit delegation.
No Gmail credentials are copied; each job uses the connected native Gmail tools.
"""
import argparse
import fcntl
import json
import os
import signal
import socket
import ssl
import subprocess
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from delivery_budget import connect, status
from manual_campaign import read_state, sent_count

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
CODEX = Path.home() / '.local/bin/codex'
TZ = ZoneInfo('Asia/Tokyo')


def online():
    """Check actual TLS reachability, not merely Wi-Fi association or DNS."""
    try:
        context = ssl.create_default_context()
        for host in ('chatgpt.com', 'gmail.googleapis.com'):
            with socket.create_connection((host, 443), timeout=5) as connection:
                with context.wrap_socket(connection, server_hostname=host):
                    pass
        return True
    except (OSError, ssl.SSLError):
        return False


def atomic_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def command(output):
    return [str(CODEX), '-a', 'never', '-s', 'workspace-write', '--search',
            'exec', '-C', str(PROJECT), '--json', '-o', str(output), '-']


def stop_child(process):
    if process.poll() is not None:
        return
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()


def wait_online(stop, record, probe=online, sleep=time.sleep):
    while not probe():
        record('waiting_for_connection')
        if stop():
            return False
        sleep(5)
    return not stop()


def next_action(budget, count, target):
    # Pending delivery always takes precedence over a full budget or completion.
    if budget['pending']:
        return 'reconcile'
    if count >= target:
        return 'complete'
    if budget['remaining'] == 0:
        return 'limit_reached'
    return 'send_one'


def prompt(campaign, action):
    rules = (ROOT / 'NIGHTLY.md').read_text()
    if action == 'reconcile':
        return (
            f'Read AGENTS.md and local-web-sales/SKILL.md. Campaign {campaign}. '
            'READ-ONLY GMAIL RECONCILIATION ONLY: never send, create or update drafts, '
            'generate images, or delete/clear pending reservations. Read the saved campaign '
            'artifacts, pending SQLite reservation and relevant Gmail Sent and Drafts. '
            'If exactly one matching sent message is positively verified, including sender, '
            'recipient, subject and both inline images, confirm it using delivery_budget.py '
            'and update that existing ledger row and website review with the real sent ID '
            'and timestamp. Otherwise leave the reservation pending and report the blocker. '
            'Never infer non-delivery from an empty search. No other work.\n' + rules
        )
    return (
        'The user explicitly authorized this one ongoing outreach campaign, including '
        'the sequential delegated execution. This is not a recurring or nightly schedule. '
        f'Campaign ID: {campaign}. Process exactly ONE new company fully and verify ONE '
        'sent message, then finish. Save research and all checkpoints under '
        f'local-web-sales/daily-outreach/runs/{campaign}/website-reviews/. '
        'Follow all current repository requirements, no follow-ups. If this invocation '
        'cannot verify one delivery, return the exact blocker, do not loosen criteria. '
        'A single unsuitable candidate is not a campaign blocker: record it as held/skipped '
        'and keep researching different qualifying candidates until one verified send '
        'or a concrete account/tool/quota blocker. Rotate regions and industries using '
        'the prior campaign website-reviews; do not repeatedly inspect a held candidate. '
        'After the earlier permission rejection, the user has now saved an explicit '
        'Always allow browsing site permission for https://www.google.com in the app '
        'and confirmed 「追加しもう絶対止まんないでね」. The user also requested '
        '「はいもう終わるまで止めないでください。 /goal」. In the parent conversation '
        'a new Maps lookup succeeded following that approval. Browser IDs are runtime-local: '
        'the parent has Chrome ID 2, while this CLI runtime advertises only Chrome ID 1. '
        'Discover the available Chrome browser in YOUR runtime and use its advertised ID '
        'for public website/Google Maps research. Do not try unavailable parent browser '
        'IDs or the unavailable iab browser. Read browser documentation and name the '
        'session before opening research tabs, then use the documented browser APIs. '
        'Treat any NEW permission rejection as a blocker; never circumvent it. '
        'For sender identity, use the native Gmail get_profile and read_email tools: '
        'the existing campaign message 1a1583ed6a0f19d1 was sent and read back '
        'as the required contact.designdan@gmail.com with the required Reply-To. '
        'Read that message to confirm the alias, then verify From/Reply-To on the '
        'newly created draft and on the actual sent message. Do not open Gmail settings '
        'or change account settings; access to that settings page was denied. '
        'Do not launch additional agents or background processes.\n' + rules
    )


def run(target):
    state = read_state()
    if not state:
        raise RuntimeError('Start a user-authorized campaign first')
    campaign = state['campaign_id']
    folder = ROOT / 'runs' / campaign / 'recovery'
    folder.mkdir(parents=True, exist_ok=True)
    report = {'campaign_id': campaign, 'pid': os.getpid(), 'target': target,
              'started_at': datetime.now(TZ).isoformat(), 'status': 'starting'}
    report_path = folder / 'status.json'
    stop_path = folder / 'STOP'
    lock = (ROOT / 'resumable.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def record(value):
        report.update(status=value, updated_at=datetime.now(TZ).isoformat(),
                      verified_sent=sent_count(campaign))
        atomic_json(report_path, report)

    child = None
    try:
        while not stop_path.exists():
            if not wait_online(stop_path.exists, record):
                break
            with connect() as database:
                budget = status(database)
            before = sent_count(campaign)
            action = next_action(budget, before, target)
            report['budget'] = budget
            if action in ('complete', 'limit_reached'):
                record(action)
                return 0
            # Do not compete with a runner holding the historical delivery lock.
            with (ROOT / 'daily.lock').open('a') as guard:
                fcntl.flock(guard, fcntl.LOCK_EX | fcntl.LOCK_NB)
            sequence = datetime.now(TZ).strftime('%Y%m%d-%H%M%S-%f')
            output = folder / f'{sequence}-{action}.txt'
            record(action)
            interrupted = False
            with (folder / f'{sequence}-events.jsonl').open('w') as log:
                child = subprocess.Popen(command(output), cwd=PROJECT,
                                         stdin=subprocess.PIPE, stdout=log, stderr=log,
                                         text=True, start_new_session=True)
                child.stdin.write(prompt(campaign, action))
                child.stdin.close()
                started = time.monotonic()
                while child.poll() is None:
                    if stop_path.exists():
                        stop_child(child)
                        break
                    if not online():
                        stop_child(child)
                        interrupted = True
                        record('waiting_for_connection')
                        break
                    if time.monotonic() - started > 1800:
                        stop_child(child)
                        record('job_timeout_needs_review')
                        return 1
                    time.sleep(5)
            if stop_path.exists():
                break
            if interrupted:
                # Re-evaluate SQLite on reconnect; never blindly repeat a send.
                continue
            with connect() as database:
                after = status(database)
            current = sent_count(campaign)
            if action == 'reconcile':
                if after['pending']:
                    record('uncertain_delivery_needs_review')
                    return 1
                # Positive reconciliation may have increased the ledger count.
                continue
            if child.returncode != 0 or after['pending'] or current != before + 1:
                record('job_stopped_needs_review')
                return 1
            record('sent_verified')
        record('stopped_by_request')
        return 0
    except Exception as error:
        report['error'] = str(error)
        record('error_needs_review')
        return 1
    finally:
        if child is not None:
            stop_child(child)
        lock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--target', type=int, default=450, choices=range(1, 451))
    args = parser.parse_args()
    if args.run:
        raise SystemExit(run(args.target))
    print(json.dumps({'campaign': read_state(), 'internet_reachable': online(),
                      'starts_workers': False, 'recurring_schedule': False,
                      'run_command': 'python3 local-web-sales/daily-outreach/resumable_campaign.py --run',
                      'requires': 'Explicit user instruction to delegate to the separate Codex execution.'},
                     ensure_ascii=False, indent=2))
