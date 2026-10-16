#!/usr/bin/env python3
"""Build one unsent, two-image outreach EML from verified lead data."""
import argparse
import html
from email.message import EmailMessage
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
SENDER = "デザインダンweb制作担当 中川 <contact.designdan@gmail.com>"
CONTACT = "contact.designdan@gmail.com"
DISCLOSURE = "※画像は非公式のデザイン案です。写真はイメージで、実際の店舗・設備を示すものではありません。"


def build(args):
    folder = ROOT / "assets" / args.date / args.slug
    folder.mkdir(parents=True, exist_ok=True)
    for name, source in (("home", args.home), ("inquiry", args.inquiry)):
        dest = folder / f"{name}.jpg"
        if dest.exists():
            raise FileExistsError(dest)
        with Image.open(source) as image:
            if name == "home" and abs(image.width / image.height - 16 / 9) > .03:
                raise ValueError("Homepage image is not 16:9")
            output = image.convert("RGB")
            output.thumbnail((1200, 675))
            output.save(dest, "JPEG", quality=72, optimize=True)

    intro = (f"{args.region}で{args.service}を探している方に、事業内容や相談方法が分かりやすく伝わるWebサイトを考え、"
             f"公開情報をもとに{args.company}様向けの画面案を作成しました。"
             f"トップ画面と{args.second_label}の画像を、このメールに掲載しています。")
    opening = "突然のご連絡失礼いたします。フリーランスでweb制作をしている中川と申します。"
    closing = ("画面案をご覧いただき、少しでもご関心がありましたら、掲載したい内容を伺ったうえで、"
               "必要なページや制作範囲、概算費用をご案内します。ご返信いただければ幸いです。")
    salutation = f"{args.company} ご担当者様"
    plain = "\n\n".join((salutation, opening, intro, closing, DISCLOSURE, f"中川\n{CONTACT}")) + "\n"
    esc = html.escape
    cid1, cid2 = f"{args.slug}-home", f"{args.slug}-inquiry"
    web = (f'<html lang="ja"><body style="font:15px/1.8 sans-serif;color:#17232b;max-width:690px">'
           f'<p>{esc(salutation)}</p><p>{esc(opening)}</p><p>{esc(intro)}</p>'
           f'<p><strong>トップ画面案</strong></p><img src="cid:{cid1}" alt="{esc(args.company)}向け非公式トップ画面案" width="650" style="max-width:100%;height:auto">'
           f'<p><strong>{esc(args.second_label)}案</strong></p><img src="cid:{cid2}" alt="{esc(args.company)}向け非公式{esc(args.second_label)}案" width="650" style="max-width:100%;height:auto">'
           f'<p>{esc(closing)}</p><p>{esc(DISCLOSURE)}</p><p>中川<br>{CONTACT}</p></body></html>')
    msg = EmailMessage()
    msg["From"] = SENDER
    msg["Reply-To"] = CONTACT
    msg["To"] = f"{args.company} ご担当者様 <{args.email}>"
    msg["Subject"] = f"{args.company}様向けWebサイト画面案のご提案"
    msg["X-Unsent"] = "1"
    msg.set_content(plain)
    msg.add_alternative(web, subtype="html")
    for name, cid in (("home", cid1), ("inquiry", cid2)):
        msg.get_payload()[1].add_related((folder / f"{name}.jpg").read_bytes(), maintype="image", subtype="jpeg", cid=f"<{cid}>", filename=f"{name}.jpg", disposition="inline")
    out = ROOT / "eml" / args.date / f"{args.slug}.eml"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise FileExistsError(out)
    out.write_bytes(msg.as_bytes())
    print(out)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for field in ("date", "slug", "company", "region", "service", "second_label", "email", "home", "inquiry"):
        p.add_argument(f"--{field.replace('_', '-')}", required=True)
    build(p.parse_args())
