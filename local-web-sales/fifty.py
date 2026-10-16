#!/usr/bin/env python3
"""Build and check 50 unsent local proposal emails."""

import argparse
import csv
import re
import shutil
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import parseaddr
from html import escape
from pathlib import Path

from cli import CAMPAIGNS, checked_message
from demo_builder import build_all, IMAGES
from sender import INTRO_NAME, SENDER_EMAIL, SENDER_NAME, SIGNATURE, SIGNATURE_HTML

ROOT = Path(__file__).resolve().parent
LEADS = ROOT / "leads.csv"
DRAFTS = ROOT / "drafts"
IMAGEGEN_ORIGINALS = ROOT / "imagegen-originals"
FIELDS = ("name", "area", "email", "email_source_url", "website_check", "checked_at")
EXPECTED_COUNT = 50


def load_leads():
    with LEADS.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("leads.csv の列が想定と異なります")
        leads = list(reader)
    if len(leads) != EXPECTED_COUNT - len(CAMPAIGNS):
        raise ValueError("追加候補は42件必要です")
    seen = {address.lower() for _, address, _ in CAMPAIGNS.values()}
    for number, lead in enumerate(leads, 1):
        if any(not lead[field].strip() for field in FIELDS):
            raise ValueError(f"候補{number}: 空欄があります")
        address = lead["email"].strip().lower()
        if parseaddr(address)[1] != address or "@" not in address or address in seen:
            raise ValueError(f"候補{number}: メールアドレスが不正または重複しています")
        if not lead["email_source_url"].startswith("https://www.tossnet.or.jp/"):
            raise ValueError(f"候補{number}: 公開メールの出典を確認してください")
        seen.add(address)
    return leads


def lead_message(lead, number):
    name, area, recipient = (lead[key].strip() for key in ("name", "area", "email"))
    region_match = re.match(r"^.+?[区市]", area)
    if not region_match:
        raise ValueError(f"{name}: 所在地から地域名を取得できません")
    region = region_match.group()
    message = EmailMessage(policy=policy.SMTP)
    message["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    message["Reply-To"] = SENDER_EMAIL
    message["To"] = f"{name} <{recipient}>"
    message["Subject"] = f"{name}様向けWebサイト画面案のご提案"
    message["X-Unsent"] = "1"
    intro = (
        f"{region}で車の整備先を探している方に、事業内容や相談方法が分かりやすく伝わるWebサイトを考え、"
        f"公開情報をもとに{name}様向けの画面案を作成しました。"
        "トップ画面とお問い合わせ画面の画像を、このメールに掲載しています。"
    )
    close = (
        "画面案をご覧いただき、少しでもご関心がありましたら、掲載したい内容を伺ったうえで、"
        "必要なページや制作範囲、概算費用をご案内します。ご返信いただければ幸いです。"
    )
    note = "※画像は非公式のデザイン案です。写真はイメージで、実際の店舗・設備を示すものではありません。"
    message.set_content(
        f"{name} ご担当者様\n\n"
        f"突然のご連絡失礼いたします。{INTRO_NAME}と申します。\n\n"
        f"{intro}\n\n{close}\n\n{note}\n\n{SIGNATURE}\n"
    )
    message.add_alternative(
        '<html lang="ja"><body style="font:15px/1.8 sans-serif;color:#17232b">'
        f"<p>{escape(name)} ご担当者様</p>"
        f"<p>突然のご連絡失礼いたします。{escape(INTRO_NAME)}と申します。</p>"
        f"<p>{escape(intro)}</p>"
        f'<p><strong>トップ画面案</strong></p><img src="cid:lead-{number:02d}-home" width="650" alt="{escape(name)}向け非公式トップ画面案" style="max-width:100%;height:auto">'
        f'<p><strong>お問い合わせ画面案</strong></p><img src="cid:lead-{number:02d}-form" width="650" alt="{escape(name)}向け非公式お問い合わせ画面案" style="max-width:100%;height:auto">'
        f"<p>{escape(close)}</p><p>{escape(note)}</p>"
        f"<p>{SIGNATURE_HTML}</p></body></html>",
        subtype="html",
    )
    html_part = message.get_payload()[-1]
    for kind in ("home", "form"):
        path = IMAGES / f"{number:02d}-{kind}.jpg"
        html_part.add_related(
            path.read_bytes(), maintype="image", subtype="jpeg",
            cid=f"<lead-{number:02d}-{kind}>", filename=path.name,
            disposition="inline",
        )
    return message


def expected():
    originals = [(f"{number:02d}-{slug}.eml", address)
                 for number, (slug, (_, address, _)) in enumerate(CAMPAIGNS.items(), 1)]
    leads = [(f"{number:02d}-lead.eml", lead["email"].strip())
             for number, lead in enumerate(load_leads(), len(originals) + 1)]
    return originals + leads


def build():
    leads = load_leads()
    build_all(leads, len(CAMPAIGNS) + 1)
    missing = [str(IMAGES / f"{number:02d}-{kind}.jpg")
               for number in range(len(CAMPAIGNS) + 1, EXPECTED_COUNT + 1)
               for kind in ("home", "form")
               if (not (IMAGES / f"{number:02d}-{kind}.jpg").is_file()
                   or not (IMAGEGEN_ORIGINALS / f"{number:02d}-{kind}.png").is_file())]
    if missing:
        raise FileNotFoundError("デモ画像が不足しています: " + ", ".join(missing))
    DRAFTS.mkdir(exist_ok=True)
    for number, (slug, (path, _, _)) in enumerate(CAMPAIGNS.items(), 1):
        checked_message(slug)
        shutil.copyfile(path, DRAFTS / f"{number:02d}-{slug}.eml")
    for number, lead in enumerate(leads, len(CAMPAIGNS) + 1):
        (DRAFTS / f"{number:02d}-lead.eml").write_bytes(lead_message(lead, number).as_bytes())
    with (DRAFTS / "index.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("file", "company", "email", "source"))
        for name, recipient in expected():
            message = BytesParser(policy=policy.default).parsebytes((DRAFTS / name).read_bytes())
            writer.writerow((name, parseaddr(message["To"])[0], recipient,
                             "existing-demo" if int(name[:2]) <= len(CAMPAIGNS) else "tossnet"))
    check()


def check():
    expected_files = expected()
    actual = {path.name for path in DRAFTS.glob("*.eml")}
    if actual != {name for name, _ in expected_files}:
        raise ValueError("下書きファイルの数または名前が想定と異なります")
    for name, recipient in expected_files:
        message = BytesParser(policy=policy.default).parsebytes((DRAFTS / name).read_bytes())
        if parseaddr(message["From"]) != (SENDER_NAME, SENDER_EMAIL):
            raise ValueError(f"{name}: 差出人が違います")
        if parseaddr(message["Reply-To"])[1] != SENDER_EMAIL:
            raise ValueError(f"{name}: 返信先が違います")
        if parseaddr(message["To"])[1].lower() != recipient.lower():
            raise ValueError(f"{name}: 宛先が違います")
        if message["X-Unsent"] != "1":
            raise ValueError(f"{name}: 未送信フラグがありません")
        bodies = [part.get_content() for part in message.walk()
                  if part.get_content_type() in ("text/plain", "text/html")]
        if len(bodies) != 2 or any(SENDER_EMAIL not in body or INTRO_NAME not in body for body in bodies):
            raise ValueError(f"{name}: 本文の名乗り・連絡先が違います")
        images = [part for part in message.walk() if part.get_content_type() == "image/jpeg"]
        if len(images) != 2:
            raise ValueError(f"{name}: デモ画像が2点ありません")
        html_body = next(part.get_content() for part in message.walk()
                         if part.get_content_type() == "text/html")
        for image in images:
            cid = image["Content-ID"].strip("<>")
            if f"cid:{cid}" not in html_body or not image.get_payload(decode=True):
                raise ValueError(f"{name}: デモ画像が本文に埋め込まれていません")
    print(f"{len(expected_files)}通の未送信.emlを確認: {DRAFTS}")


def check_daily(path, recipient):
    """Check one independently researched daily outreach message."""
    message = BytesParser(policy=policy.default).parsebytes(Path(path).read_bytes())
    if parseaddr(message["From"]) != (SENDER_NAME, SENDER_EMAIL):
        raise ValueError("差出人が違います")
    if parseaddr(message["Reply-To"])[1] != SENDER_EMAIL:
        raise ValueError("返信先が違います")
    if parseaddr(message["To"])[1].casefold() != recipient.casefold():
        raise ValueError("宛先が違います")
    if message["X-Unsent"] != "1":
        raise ValueError("未送信フラグがありません")
    if not message["Subject"]:
        raise ValueError("件名がありません")
    bodies = {part.get_content_type(): part.get_content() for part in message.walk()
              if part.get_content_type() in ("text/plain", "text/html")}
    if set(bodies) != {"text/plain", "text/html"}:
        raise ValueError("本文の形式が不足しています")
    for body in bodies.values():
        normalized_body = body.replace("\r\n", "\n")
        if SIGNATURE not in normalized_body.replace("<br>", "\n") and SIGNATURE_HTML not in normalized_body:
            raise ValueError("署名が違います")
        if "非公式" not in body or "写真はイメージ" not in body:
            raise ValueError("画像の注意書きがありません")
    images = [part for part in message.walk() if part.get_content_type() == "image/jpeg"]
    if len(images) != 2:
        raise ValueError("画像が2点ではありません")
    html_body = bodies["text/html"]
    for image in images:
        cid = image["Content-ID"].strip("<>")
        if f"cid:{cid}" not in html_body or not image.get_payload(decode=True):
            raise ValueError("画像がインラインで埋め込まれていません")
    print(f"1通の未送信.emlを確認: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="50通のローカル未送信メール")
    parser.add_argument("command", choices=("build", "check", "check-daily"))
    parser.add_argument("--path")
    parser.add_argument("--to")
    args = parser.parse_args()
    if args.command == "check-daily":
        if not args.path or not args.to:
            parser.error("check-daily requires --path and --to")
        check_daily(args.path, args.to)
    else:
        (build if args.command == "build" else check)()
