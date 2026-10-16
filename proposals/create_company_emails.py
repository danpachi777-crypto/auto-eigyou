"""Build five unsent outreach emails with company-specific inline mockups."""

from email.message import EmailMessage
from email.policy import SMTP
from html import escape
from pathlib import Path
from sender import INTRO_NAME, SENDER_EMAIL, SENDER_NAME, SIGNATURE, SIGNATURE_HTML


ROOT = Path(__file__).resolve().parent
IMAGE_DIR = ROOT / "email-images"

COMPANIES = (
    ("toun", "東運整備株式会社", "tohun.s-0571@fancy.ocn.ne.jp", "板橋区板橋"),
    ("toshima", "豊島小型自動車株式会社", "tkj-2@alto.ocn.ne.jp", "板橋区板橋"),
    ("kyowa", "有限会社協和自動車整備", "km@kyowa-net.com", "葛飾区東立石"),
    ("kimura", "有限会社木村自動車工業", "ikeo-auto-mobile@kde.biglobe.ne.jp", "大田区大森南"),
    ("kworks", "K-WORKS", "kugemoto@viver.sannet.ne.jp", "杉並区本天沼"),
)


def build(slug: str, name: str, recipient: str, area: str) -> Path:
    message = EmailMessage(policy=SMTP)
    message["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    message["Reply-To"] = SENDER_EMAIL
    message["To"] = f"{name} <{recipient}>"
    message["Subject"] = f"{name}様向けWebサイト画面案のご提案"
    message["X-Unsent"] = "1"

    intro = (
        f"{area}で車の整備先を探している方に、事業内容や相談方法が分かりやすく伝わるWebサイトを考え、"
        f"公開情報をもとに{name}様向けの画面案を作成しました。"
        "トップ画面と予約希望の確認フォームの画像を、このメールに掲載しています。"
    )
    close = (
        "画面案をご覧いただき、少しでもご関心がありましたら、掲載したい内容を伺ったうえで、"
        "必要なページや制作範囲、概算費用をご案内します。ご返信いただければ幸いです。"
    )
    note = "※画像は非公式のデザイン案です。写真はイメージで、実際の店舗・設備を示すものではありません。"

    message.set_content(
        f"""{name} ご担当者様

突然のご連絡失礼いたします。{INTRO_NAME}と申します。

{intro}

{close}

{note}

{SIGNATURE}
"""
    )

    html = f"""\
<html lang="ja"><body style="margin:0;padding:24px;color:#17232b;font:15px/1.8 -apple-system,BlinkMacSystemFont,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif">
<div style="max-width:650px;margin:auto">
<p>{escape(name)} ご担当者様</p>
<p>突然のご連絡失礼いたします。{escape(INTRO_NAME)}と申します。</p>
<p>{escape(intro)}</p>
<p style="margin:24px 0 8px;font-weight:bold">トップ画面案</p>
<img src="cid:{slug}-home" alt="{escape(name)}向け非公式トップ画面案" width="650" style="display:block;width:100%;max-width:650px;height:auto;border:1px solid #dce2dc">
<p style="margin:24px 0 8px;font-weight:bold">予約希望の確認フォーム案</p>
<img src="cid:{slug}-form" alt="{escape(name)}向け非公式フォーム画面案" width="650" style="display:block;width:100%;max-width:650px;height:auto;border:1px solid #dce2dc">
<p>{escape(close)}</p>
<p>{escape(note)}</p>
<p>{SIGNATURE_HTML}</p>
</div></body></html>"""
    message.add_alternative(html, subtype="html")
    html_part = message.get_payload()[-1]
    for kind in ("home", "form"):
        image = IMAGE_DIR / f"{slug}-{kind}.jpg"
        html_part.add_related(
            image.read_bytes(),
            maintype="image",
            subtype="jpeg",
            cid=f"<{slug}-{kind}>",
            filename=image.name,
            disposition="inline",
        )

    output = ROOT / ("toun-seibi-email.eml" if slug == "toun" else f"{slug}-email.eml")
    output.write_bytes(message.as_bytes())
    return output


if __name__ == "__main__":
    for company in COMPANIES:
        print(build(*company))
