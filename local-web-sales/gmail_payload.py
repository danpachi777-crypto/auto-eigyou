#!/usr/bin/env python3
"""Print a Gmail draft payload for one local .eml without sending it."""

import base64
import json
import sys
from email import policy
from email.parser import BytesParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRAFTS = ROOT / "drafts"
sys.path.insert(0, str(ROOT.parent / "proposals"))
from sender import SENDER_EMAIL


def part_payload(part):
    result = {"mime_type": part.get_content_type()}
    if part.is_multipart():
        result["parts"] = [part_payload(child) for child in part.iter_parts()]
        return result
    if part.get_content_maintype() == "text":
        result["body"] = {"content": part.get_content()}
        result["charset"] = part.get_content_charset() or "utf-8"
    else:
        result["body"] = {
            "base64_url_content": base64.urlsafe_b64encode(part.get_payload(decode=True)).decode().rstrip("=")
        }
    if part.get_filename():
        result["filename"] = part.get_filename()
    if part.get("Content-ID"):
        result["content_id"] = part["Content-ID"].strip("<>")
    if part.get_content_disposition():
        result["content_disposition"] = part.get_content_disposition()
    return result


def main():
    if len(sys.argv) != 2 or Path(sys.argv[1]).name != sys.argv[1]:
        raise ValueError("drafts内のファイル名を1つ指定してください")
    path = DRAFTS / sys.argv[1]
    message = BytesParser(policy=policy.default).parsebytes(path.read_bytes())
    if SENDER_EMAIL not in str(message["From"]):
        raise ValueError("送信元が想定と異なります")
    print(json.dumps({
        "from_address": str(message["From"]),
        "reply_to": str(message["Reply-To"]),
        "to": str(message["To"]),
        "subject": str(message["Subject"]),
        "payload": part_payload(message),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
