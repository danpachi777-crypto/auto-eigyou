#!/usr/bin/env python3
"""Local proposal email builder, checker, and optional SMTP sender."""

import argparse
import getpass
import smtplib
import ssl
import sys
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPOSALS = ROOT / "proposals"
sys.path.insert(0, str(PROPOSALS))
from sender import INTRO_NAME, SENDER_EMAIL, SENDER_NAME
from create_company_emails import COMPANIES as AUTO_COMPANIES, build as build_auto

OTHER_DIR = PROPOSALS / "other-industries"
sys.path.insert(0, str(OTHER_DIR))
from create_emails import COMPANIES as OTHER_COMPANIES, build as build_other

CAMPAIGNS = {
    **{
        slug: (PROPOSALS / ("toun-seibi-email.eml" if slug == "toun" else f"{slug}-email.eml"), address, "auto")
        for slug, _, address, _ in AUTO_COMPANIES
    },
    **{
        slug: (OTHER_DIR / f"{slug}-email.eml", address, "other")
        for slug, _, address, *_ in OTHER_COMPANIES
    },
}


def selected(args):
    if args.company:
        return [args.company]
    return [slug for slug, (_, _, group) in CAMPAIGNS.items() if args.group == "all" or group == args.group]


def build(slugs):
    details = {company[0]: (company, build_auto) for company in AUTO_COMPANIES}
    details.update({company[0]: (company, build_other) for company in OTHER_COMPANIES})
    for slug in slugs:
        company, builder = details[slug]
        print(builder(*company))


def checked_message(slug):
    path, expected_recipient, _ = CAMPAIGNS[slug]
    message = BytesParser(policy=policy.SMTP).parsebytes(path.read_bytes())
    if parseaddr(message["From"])[1].lower() != SENDER_EMAIL:
        raise ValueError(f"{slug}: 送信元メールアドレスが違います")
    if parseaddr(message["From"])[0] != SENDER_NAME:
        raise ValueError(f"{slug}: 送信元の屋号・氏名が違います")
    if parseaddr(message["Reply-To"])[1].lower() != SENDER_EMAIL:
        raise ValueError(f"{slug}: 返信先メールアドレスが違います")
    if parseaddr(message["To"])[1].lower() != expected_recipient:
        raise ValueError(f"{slug}: 宛先が原稿と一致しません")
    if "X-Unsent" in message:
        del message["X-Unsent"]
    content_parts = [p.get_content() for p in message.walk() if p.get_content_type() in ("text/plain", "text/html")]
    if len(content_parts) != 2 or any("[屋号・氏名]" in body or "[連絡先]" in body for body in content_parts):
        raise ValueError(f"{slug}: 本文が未完成です")
    if any(INTRO_NAME not in body or SENDER_EMAIL not in body for body in content_parts):
        raise ValueError(f"{slug}: 屋号・氏名・連絡先が本文にありません")
    if len([p for p in message.walk() if p.get_content_type() == "image/jpeg"]) != 2:
        raise ValueError(f"{slug}: 画像が2点ありません")
    return message, expected_recipient


def main():
    parser = argparse.ArgumentParser(description="local-web-sales: ローカル提案メール管理")
    parser.add_argument("command", choices=("build", "check", "auth", "send"), help="原稿生成・確認・SMTP認証・送信")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--group", choices=("auto", "other", "all"), default="all")
    scope.add_argument("--company", choices=CAMPAIGNS)
    args = parser.parse_args()
    if args.command == "auth":
        password = getpass.getpass(f"{SENDER_EMAIL} のGoogleアプリパスワード: ")
        if not password:
            raise ValueError("アプリパスワードが入力されていません")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as smtp:
            smtp.login(SENDER_EMAIL, password)
        print(f"認証成功: {SENDER_EMAIL}（メールは送信していません）")
        return
    slugs = selected(args)
    if args.command == "build":
        build(slugs)
    prepared = [(slug, *checked_message(slug)) for slug in slugs]
    for slug, message, recipient in prepared:
        print(f"{slug}: {SENDER_NAME} <{SENDER_EMAIL}> -> {recipient} | {message['Subject']}")
    if args.command != "send":
        print(f"{len(prepared)}通を確認。送信はしていません。")
        return
    print("この操作は実際にメールを送信します。")
    if input("送信する場合は SEND と入力: ").strip() != "SEND":
        print("送信を中止しました。")
        return
    password = getpass.getpass(f"{SENDER_EMAIL} のGoogleアプリパスワード: ")
    if not password:
        raise ValueError("アプリパスワードが入力されていません")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as smtp:
        smtp.login(SENDER_EMAIL, password)
        for slug, message, recipient in prepared:
            smtp.send_message(message, from_addr=SENDER_EMAIL, to_addrs=[recipient])
            print(f"送信済み: {slug} -> {recipient}")


if __name__ == "__main__":
    main()
