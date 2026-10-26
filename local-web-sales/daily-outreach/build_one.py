#!/usr/bin/env python3
"""Build one unsent, two-image outreach EML from verified lead data."""
import argparse
import html
import json
import subprocess
import struct
from email.message import EmailMessage
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None


ROOT = Path(__file__).resolve().parent
SENDER = "デザインダンweb制作担当 中川 <contact.designdan@gmail.com>"
CONTACT = "contact.designdan@gmail.com"
DISCLOSURE = "※画像は非公式のデザイン案です。写真はイメージで、実際の店舗・設備を示すものではありません。"
OFFER = ROOT / "offer.json"


def proposal_copy(args):
    """Use one observed issue; never invent commercial terms."""
    review = json.loads(Path(args.website_review).read_text())
    if review.get("company") != args.company or review.get("priority") not in ("high", "medium"):
        raise ValueError("A reviewed, eligible website finding for this company is required")
    findings = review.get("findings", [])
    if args.finding_index < 0 or args.finding_index >= len(findings):
        raise ValueError("Choose exactly one existing website finding")
    finding = findings[args.finding_index]
    if not all(isinstance(finding.get(k), str) and finding[k].strip()
               for k in ("url", "observation", "proposal")):
        raise ValueError("The finding needs an observed fact, URL and concrete proposal")
    offer = json.loads(OFFER.read_text())
    scope = offer.get("allowed_scope") if offer.get("scope_confirmed") else None
    if scope:
        scope_text = f"対応できる制作範囲は、{scope}です。今回はその中から、上記の改善をご提案します。"
    else:
        scope_text = "今回は上記の改善に範囲を絞ったご提案です。対応範囲は現在のサイトの仕様を伺ったうえで確認します。"
    terms = []
    for label, confirmed, key in (("費用目安", "price_confirmed", "price_text"),
                                  ("納期目安", "turnaround_confirmed", "turnaround_text")):
        value = offer.get(key)
        if offer.get(confirmed):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Confirmed {label} is missing")
            terms.append(f"{label}：{value}")
        else:
            terms.append(f"{label}：対象範囲とサイトの仕様を確認後、個別にご案内します。")
    observation = f"御社のWebサイトを拝見し、次の点を確認しました。\n{finding['observation']}"
    intro = (f"{finding['proposal']}という改善を考え、公開情報をもとに{args.company}様向けの画面案を作成しました。"
             f"トップ画面と{args.second_label}の画像を、このメールに掲載しています。")
    return observation, intro, scope_text + "\n" + "\n".join(terms), "この部分の見直しは、現在ご検討されていますか？"


def build(args):
    from storage_guard import reclaim
    reclaim()
    observation, intro, terms, closing = proposal_copy(args)
    folder = ROOT / "assets" / args.date / args.slug
    folder.mkdir(parents=True, exist_ok=True)
    for name, source in (("home", args.home), ("inquiry", args.inquiry)):
        dest = folder / f"{name}.jpg"
        if dest.exists():
            raise FileExistsError(dest)
        if Image is not None:
            with Image.open(source) as image:
                if name == "home" and abs(image.width / image.height - 16 / 9) > .03:
                    raise ValueError("Homepage image is not 16:9")
                output = image.convert("RGB")
                output.thumbnail((1200, 675))
                output.save(dest, "JPEG", quality=72, optimize=True)
        else:
            data = Path(source).read_bytes()
            if data[:8] != b"\x89PNG\r\n\x1a\n":
                raise ValueError("Without Pillow, source must be PNG")
            width, height = struct.unpack(">II", data[16:24])
            if name == "home" and abs(width / height - 16 / 9) > .03:
                raise ValueError("Homepage image is not 16:9")
            subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "72",
                            "-Z", "1200", str(source), "--out", str(dest)],
                           check=True, capture_output=True)

    opening = "突然のご連絡失礼いたします。フリーランスでweb制作をしている中川と申します。"
    salutation = f"{args.company} ご担当者様"
    plain = "\n\n".join((salutation, opening, observation, intro, terms, closing, DISCLOSURE, f"中川\n{CONTACT}")) + "\n"
    esc = html.escape
    cid1, cid2 = f"{args.slug}-home", f"{args.slug}-inquiry"
    web = (f'<html lang="ja"><body style="font:15px/1.8 sans-serif;color:#17232b;max-width:690px">'
           f'<p>{esc(salutation)}</p><p>{esc(opening)}</p><p>{esc(observation).replace(chr(10), "<br>")}</p><p>{esc(intro)}</p>'
           f'<p><strong>トップ画面案</strong></p><img src="cid:{cid1}" alt="{esc(args.company)}向け非公式トップ画面案" width="650" style="max-width:100%;height:auto">'
           f'<p><strong>{esc(args.second_label)}案</strong></p><img src="cid:{cid2}" alt="{esc(args.company)}向け非公式{esc(args.second_label)}案" width="650" style="max-width:100%;height:auto">'
           f'<p>{esc(terms).replace(chr(10), "<br>")}</p><p>{esc(closing)}</p><p>{esc(DISCLOSURE)}</p><p>中川<br>{CONTACT}</p></body></html>')
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
    p.add_argument("--website-review", required=True, help="Evidence-backed website review JSON")
    p.add_argument("--finding-index", type=int, default=0, help="One verified issue to propose fixing")
    build(p.parse_args())
