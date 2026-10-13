"""Create unsent, image-rich proposal emails for three other industries."""

from email.message import EmailMessage
from email.policy import SMTP
from html import escape
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sender import INTRO_NAME, SENDER_EMAIL, SENDER_NAME, SIGNATURE, SIGNATURE_HTML


ROOT = Path(__file__).resolve().parent
IMAGE_DIR = ROOT / "email-images"
COMPANIES = (
    (
        "rescue151a",
        "くらしのレスキュー 151a",
        "rescue151a@gmail.com",
        "東京都江東区",
        "便利屋・ハウスクリーニング",
        "見積り相談の確認画面",
    ),
    (
        "tailor_doi",
        "テーラードイ",
        "doiman0101@yahoo.co.jp",
        "大阪市阿倍野区",
        "仕立屋",
        "来店相談の確認画面",
    ),
    (
        "hair_jun",
        "ヘアーファクトリーＪＵＮ",
        "hair_factory_jun@yahoo.co.jp",
        "熊本市西区",
        "理容店",
        "予約希望の確認画面",
    ),
)


def build(
    slug: str,
    name: str,
    recipient: str,
    area: str,
    industry: str,
    form_label: str,
) -> Path:
    message = EmailMessage(policy=SMTP)
    message["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    message["Reply-To"] = SENDER_EMAIL
    message["To"] = f"{name} <{recipient}>"
    message["Subject"] = f"{name}様向けウェブサイト画面案のご提案"
    message["X-Unsent"] = "1"

    intro = (
        f"{area}で{industry}を探す方に向け、公開情報と同業サイトの構成を参考に、"
        f"{name}様向けのウェブサイト画面案を作成しました。"
    )
    note = (
        "掲載画像は非公式のデザイン案です。写真は生成したイメージで、"
        "実際の店舗・設備を示すものではありません。"
        "貴店の承認・監修を受けたものではなく、確認画面は動作しません。"
    )
    plain = f"""{name} ご担当者様

突然のご連絡失礼いたします。{INTRO_NAME}と申します。

{intro}このメールにトップ画面と{form_label}の画像を掲載しています。

{note}

ご関心がありましたら、掲載したい内容を伺い、制作範囲をご提案します。

{SIGNATURE}

掲載画像: トップ画面、{form_label}
"""
    message.set_content(plain)

    html = f"""<html lang="ja"><body style="margin:0;padding:24px;color:#17232b;font:15px/1.8 -apple-system,BlinkMacSystemFont,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif">
<div style="max-width:650px;margin:auto">
<p>{escape(name)} ご担当者様</p>
<p>突然のご連絡失礼いたします。{escape(INTRO_NAME)}と申します。</p>
<p>{escape(intro)}このメールにトップ画面と{escape(form_label)}の画像を掲載しています。</p>
<p style="margin:24px 0 8px;font-weight:bold">トップ画面案</p>
<img src="cid:{slug}-home" alt="{escape(name)}向け非公式トップ画面案" width="650" style="display:block;width:100%;max-width:650px;height:auto;border:1px solid #dce2dc">
<p style="margin:24px 0 8px;font-weight:bold">{escape(form_label)}案</p>
<img src="cid:{slug}-form" alt="{escape(name)}向け非公式確認画面案" width="650" style="display:block;width:100%;max-width:650px;height:auto;border:1px solid #dce2dc">
<p>{escape(note)}</p>
<p>ご関心がありましたら、掲載したい内容を伺い、制作範囲をご提案します。</p>
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

    output = ROOT / f"{slug}-email.eml"
    output.write_bytes(message.as_bytes())
    return output


if __name__ == "__main__":
    for company in COMPANIES:
        print(build(*company))
