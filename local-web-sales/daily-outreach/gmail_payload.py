#!/usr/bin/env python3
"""Convert a checked local EML into the connected Gmail draft tool's MIME payload."""
import base64
import json
import sys
from email import policy
from email.parser import BytesParser
from pathlib import Path


def convert(part):
    result = {"mime_type": part.get_content_type()}
    if part.is_multipart():
        result["parts"] = [convert(child) for child in part.iter_parts()]
    elif part.get_content_maintype() == "text":
        result["charset"] = "utf-8"
        result["body"] = {"content": part.get_content()}
    else:
        result["body"] = {"base64_url_content": base64.urlsafe_b64encode(part.get_payload(decode=True)).decode()}
    if part.get("Content-ID"):
        result["content_id"] = part["Content-ID"]
    if part.get_filename():
        result["filename"] = part.get_filename()
    if part.get_content_disposition():
        result["content_disposition"] = part.get_content_disposition()
    return result


msg = BytesParser(policy=policy.default).parsebytes(Path(sys.argv[1]).read_bytes())
print(json.dumps({"from_address": str(msg["From"]), "reply_to": str(msg["Reply-To"]),
                  "to": str(msg["To"]), "subject": str(msg["Subject"]),
                  "payload": convert(msg)}, ensure_ascii=False))
