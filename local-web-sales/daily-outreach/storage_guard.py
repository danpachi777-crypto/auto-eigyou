#!/usr/bin/env python3
"""Reclaim completed outreach download copies; never remove retained evidence."""
import argparse
import fcntl
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
MIN_FREE = 2 * 1024**3


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def candidates(root, downloads):
    """Completed sends or no-issue/exclusion reviews with retained PNGs."""
    indexed = {}
    for review in (root / 'runs').glob('*/website-reviews/*.json'):
        data = json.loads(review.read_text())
        status = data.get('status', '')
        completed = (status == 'sent_verified' or
                     status == 'reviewed_native_ready_for_proposal' or
                     status == 'images_verified_ready_for_draft' or
                     status == 'hold_no_verified_issue_mobile' or
                     status == 'hold_official_mobile_site_no_verified_issue' or
                     status.startswith('excluded_'))
        if not completed:
            continue
        host = urlsplit(data.get('website_url', '')).hostname
        if not host:
            continue
        evidence = review.parent.parent / 'evidence' / review.stem
        for kept in evidence.glob('*.png'):
            if kept.is_file() and not kept.is_symlink():
                indexed.setdefault(kept.stat().st_size, []).append((host.removeprefix('www.'), kept))
    for source in downloads.glob('*.png'):
        if source.is_symlink() or not source.is_file():
            continue
        # Contact pages may use an external form host. Exact retained bytes,
        # rather than the download filename, establish that a copy is expendable.
        options = indexed.get(source.stat().st_size, [])
        if not options:
            continue
        sha = digest(source)
        for _, kept in options:
            if source.resolve() != kept.resolve() and digest(kept) == sha:
                yield source, kept, sha
                break


def generated_candidates(root):
    """Recover generated working copies only when SENT originals are retained.

    Only generation session folders explicitly recorded by this project's
    prompts are scanned. Project originals and same-inode hard links stay put.
    """
    indexed, sessions = {}, set()
    generated_root = Path.home() / '.codex' / 'generated_images'
    for review in (root / 'runs').glob('*/website-reviews/*.json'):
        data = json.loads(review.read_text())
        if data.get('status') != 'sent_verified':
            continue
        for assets in (root / 'assets').glob('*/' + review.stem):
            prompts = assets / 'prompts.json'
            if prompts.is_file():
                metadata = json.loads(prompts.read_text())
                for key in ('home_original', 'inquiry_original', 'home_source', 'inquiry_source'):
                    source = metadata.get(key)
                    if isinstance(source, str):
                        parent = Path(source).parent
                        if parent.parent == generated_root and not parent.is_symlink():
                            sessions.add(parent)
            for kept in assets.glob('*-original.png'):
                if kept.is_file() and not kept.is_symlink():
                    indexed.setdefault(kept.stat().st_size, []).append(kept)
    for session in sessions:
        for source in session.glob('*.png'):
            if not source.is_file() or source.is_symlink():
                continue
            before = source.stat()
            options = [kept for kept in indexed.get(before.st_size, [])
                       if (kept.stat().st_dev, kept.stat().st_ino) !=
                       (before.st_dev, before.st_ino)]
            if not options:
                continue
            sha = digest(source)
            for kept in options:
                if digest(kept) == sha:
                    yield source, kept, sha
                    break


def reclaim(root=ROOT, downloads=None, min_free=MIN_FREE, force=False, dry_run=False):
    downloads = downloads or Path.home() / 'Downloads'
    report = {'at': datetime.now(timezone.utc).isoformat(), 'free_before': shutil.disk_usage(root).free,
              'dry_run': dry_run, 'files': [], 'freed_bytes': 0}
    if not force and report['free_before'] >= min_free:
        report['free_after'] = report['free_before']
        return report
    with (root / 'runs/storage-cleanup.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        log = root / 'runs/storage-cleanup.jsonl'
        from itertools import chain
        for source, kept, sha in chain(candidates(root, downloads), generated_candidates(root)):
            before = source.stat()
            # Recheck both copies immediately before unlinking the expendable one.
            if source.is_symlink() or kept.is_symlink() or digest(kept) != sha or digest(source) != sha:
                continue
            after = source.stat()
            if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
                continue
            event = {'at': report['at'], 'source': str(source), 'retained': str(kept),
                     'sha256': sha, 'bytes': before.st_size, 'dry_run': dry_run}
            if not dry_run:
                # Persist the recovery location before deleting anything.
                with log.open('a') as stream:
                    stream.write(json.dumps(event, ensure_ascii=False) + '\n')
                    stream.flush()
                    os.fsync(stream.fileno())
                source.unlink()
            report['files'].append(event)
            report['freed_bytes'] += before.st_size
            if not force and shutil.disk_usage(root).free >= min_free:
                break
    report['free_after'] = shutil.disk_usage(root).free
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--force', action='store_true', help='Clean eligible duplicates even above the threshold')
    args = parser.parse_args()
    result = reclaim(force=args.force, dry_run=args.dry_run)
    print(json.dumps({**result, 'files': len(result['files'])}, ensure_ascii=False))
