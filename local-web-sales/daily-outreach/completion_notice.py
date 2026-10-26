#!/usr/bin/env python3
"""Watch this campaign and relay completion/attention notices to its Codex chat.

This does not send sales emails or install a recurring schedule. Phone push
delivery also requires the user's ChatGPT app/OS notification permission.
"""
import argparse
import csv
import fcntl
import hashlib
import json
import os
import sqlite3
import subprocess
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from resumable_campaign import ROOT, command


def campaign_snapshot(campaign, root=ROOT, target=450):
    with (root / 'ledger.csv').open(newline='', encoding='utf-8-sig') as stream:
        rows = [r for r in csv.DictReader(stream) if r.get('campaign_id') == campaign]
    sent = [r for r in rows if r.get('delivery_status') == 'sent'
            and r.get('gmail_sent_message_id') and r.get('sent_at')]
    addresses = [r['email'].strip().casefold() for r in sent]
    ids = [r['gmail_sent_message_id'] for r in sent]
    if len(addresses) != len(set(addresses)) or len(ids) != len(set(ids)):
        raise ValueError('Duplicate recipients/message IDs; completion is unproven')
    if len(sent) > target:
        raise ValueError('Campaign exceeds its target; do not call it successful')
    for row in sent:
        if datetime.fromisoformat(row['sent_at']).tzinfo is None:
            raise ValueError('Unverified sent time')
    database = root / 'runs' / 'delivery-budget.sqlite3'
    with sqlite3.connect(f'file:{database}?mode=ro', uri=True) as connection:
        pending = connection.execute("SELECT email FROM deliveries WHERE status='pending'").fetchall()
        verified = {email: message_id for email, message_id in connection.execute(
            "SELECT email,message_id FROM deliveries WHERE campaign=? AND status='sent'", (campaign,))}
    matches = all(verified.get(r['email'].strip().casefold()) == r['gmail_sent_message_id'] for r in sent)
    return {'campaign_id': campaign, 'sent': len(sent), 'target': target,
            'pending': len(pending), 'ledger_database_match': matches,
            'complete': len(sent) == target and not pending and matches}


def alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except (TypeError, ValueError, ProcessLookupError):
        return False


def atomic_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def relay_prompt(thread, event, snapshot):
    marker = 'OUTREACH_NOTICE_' + event
    if event == 'test':
        message = f'【通知テスト】営業450件の完了通知設定を確認中です。現在の送信確認は{snapshot["sent"]}/450件です。まだ完了していません。'
    elif event == 'complete':
        message = '【営業450件の完了候補】台帳とSQLiteで450件が一致しました。最終Gmail確認・配信失敗の確認を行い、実際の結果をこの会話で報告してください。確認前に完了と断定しないでください。'
    else:
        message = f'【営業の中断通知】現在{snapshot["sent"]}/450件。送信処理が停止しています。runs/{snapshot["campaign_id"]}/recovery/status.jsonと直近ログを確認して、停止理由と再開に必要な操作を短く報告してください。完了とは扱わないでください。'
    followup = marker + '\n' + message
    return (
        'The user requested phone notifications for their own outreach campaign. '
        'Relay this notification to their EXISTING parent Codex conversation using '
        'codex_tui.send_message_to_thread, not email, HTTP, another account or a new task. '
        f'Target threadId: {thread}. Exact prompt to relay: {followup}\n'
        'This is a notification-only job: do not send sales mail or change any settings. '
        'If the target has an active writer, wait 20 seconds and retry the same target '
        'until it becomes idle. Do not create a new thread. If the call is rejected '
        'for another reason, stop and report the exact error. Return JSON with '
        'accepted true only if the actual send_message_to_thread call succeeded. '
        'Do not claim the phone displayed a push notification; that is not observable here.'
    )


def relay(folder, thread, event, snapshot):
    path = folder / (event + '-relay.json')
    if path.exists():
        # Do not repeat an accepted or uncertain relay after restarting the watcher.
        return
    output = folder / (event + '-result.txt')
    log_path = folder / (event + '-events.jsonl')
    with log_path.open('w') as log:
        worker = subprocess.Popen(command(output), cwd=ROOT.parents[1],
                                  stdin=subprocess.PIPE, stdout=log, stderr=log,
                                  text=True, start_new_session=True)
        worker.stdin.write(relay_prompt(thread, event, snapshot))
        worker.stdin.close()
    atomic_json(path, {'pid': worker.pid, 'event': event, 'status': 'relay_started',
                       'phone_push_verified': False, 'snapshot': snapshot})


def watch(campaign, thread, test=False):
    folder = ROOT / 'runs' / campaign / 'notifications'
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / 'watch.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        while True:
            snapshot = campaign_snapshot(campaign)
            state_path = ROOT / 'runs' / campaign / 'recovery' / 'status.json'
            controller = json.loads(state_path.read_text()) if state_path.exists() else {}
            running = alive(controller.get('pid'))
            atomic_json(folder / 'status.json', {
                **snapshot, 'watcher_pid': os.getpid(), 'controller_alive': running,
                'controller_status': controller.get('status'), 'chat_thread': thread,
                'checked_at': datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(),
                'delivery_channel': 'Codex parent chat; mobile push permission required',
                'phone_push_verified': False})
            if test:
                relay(folder, thread, 'test', snapshot)
                test = False
            if snapshot['complete']:
                relay(folder, thread, 'complete', snapshot)
                return
            if controller and not running and controller.get('status') not in ('complete',):
                event = 'attention-' + hashlib.sha256(
                    (str(controller.get('started_at')) + str(controller.get('updated_at'))).encode()).hexdigest()[:12]
                # Serialize test/attention relays to avoid two competing turns.
                test_path = folder / 'test-relay.json'
                test_running = test_path.exists() and alive(json.loads(test_path.read_text()).get('pid'))
                if not test_running:
                    relay(folder, thread, event, snapshot)
            time.sleep(20)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign', required=True)
    parser.add_argument('--chat-thread')
    parser.add_argument('--watch', action='store_true')
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()
    if args.watch:
        if not args.chat_thread:
            parser.error('--watch requires --chat-thread')
        watch(args.campaign, args.chat_thread, args.test)
    else:
        print(json.dumps(campaign_snapshot(args.campaign), ensure_ascii=False))
