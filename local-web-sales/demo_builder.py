"""Create local, nonofficial site demos for the additional outreach drafts."""

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEMOS = ROOT / "demos"
IMAGES = ROOT / "email-images"
PALETTES = (
    ("#173f3a", "#d7ad63", "#e8efe9"),
    ("#29384c", "#d5a565", "#edf1f4"),
    ("#4c302a", "#d5aa79", "#f3ece5"),
    ("#193d4b", "#85b9bd", "#e6f0ef"),
    ("#44394f", "#c3a3b4", "#f0ebf2"),
    ("#3d4028", "#cdbd76", "#f0f1e8"),
)

STYLE = """\
:root{font-family:-apple-system,BlinkMacSystemFont,'Hiragino Kaku Gothic ProN',Meiryo,sans-serif;color:#152b31;background:#f7f8f5}
*{box-sizing:border-box}body{margin:0}a{color:inherit;text-decoration:none}button,input,textarea{font:inherit}
.notice{background:#fff6dc;color:#58420e;text-align:center;padding:10px 18px;font-size:13px}
header{background:white;border-bottom:1px solid #e2e8e4;padding:20px max(24px,calc((100vw - 1120px)/2));display:flex;align-items:center;justify-content:space-between;gap:20px}
.brand{font-weight:800;letter-spacing:.02em;font-size:20px}.brand small{display:block;color:#607779;font-size:11px;font-weight:600;letter-spacing:.16em;margin-bottom:3px}
nav{display:flex;gap:28px;font-size:14px}nav a:hover{text-decoration:underline}.button{display:inline-block;background:var(--accent);color:white;padding:14px 22px;border:0;border-radius:8px;font-weight:700;cursor:pointer}
.hero{color:white;background:linear-gradient(115deg,var(--accent),#111e24);min-height:460px;position:relative;overflow:hidden}.hero:after{content:'';position:absolute;right:-6%;top:-75px;width:520px;height:520px;border:2px solid #ffffff3a;border-radius:50%;box-shadow:0 0 0 55px #ffffff0b,0 0 0 130px #ffffff08;pointer-events:none}
.wrap{max-width:1120px;margin:auto;padding:0 24px}.hero .wrap{padding-top:108px;padding-bottom:85px;position:relative;z-index:1}.eyebrow{color:var(--highlight);font-weight:700;letter-spacing:.18em;font-size:12px}.hero h1{max-width:760px;font-size:clamp(36px,5vw,64px);line-height:1.24;margin:19px 0 24px;letter-spacing:-.03em}.hero p{max-width:650px;line-height:1.9;color:#e7eeed}.hero .button{margin-top:25px;background:var(--highlight);color:#142b2c}
section{padding:68px 0}section h2{font-size:clamp(28px,3vw,38px);margin:0 0 14px}.lead{color:#5e7071;line-height:1.9;max-width:700px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:32px}.card{background:#fff;border:1px solid #e2e9e5;border-radius:14px;padding:29px;min-height:174px}.card strong{display:block;font-size:19px;margin-bottom:13px}.card p{line-height:1.8;color:#66777a;font-size:14px;margin:0}.number{font-size:12px;letter-spacing:.1em;color:var(--accent);font-weight:800}
.band{background:var(--pale)}.grid{display:grid;grid-template-columns:1fr 1fr;gap:50px;align-items:center}.panel{background:white;padding:33px;border-radius:16px;box-shadow:0 18px 45px #12312b11}.panel p{line-height:1.8;color:#52676a}
footer{background:#152b31;color:#d5e4e0;padding:35px 24px;text-align:center;font-size:13px}.form{max-width:730px;margin:38px auto 0;background:white;border:1px solid #e1e8e4;border-radius:16px;padding:38px;box-shadow:0 18px 45px #12312b0a}.form label{display:block;margin:22px 0 8px;font-weight:700}.form input,.form textarea{width:100%;border:1px solid #cbd6d2;border-radius:7px;padding:13px;background:#fdfefd}.form textarea{min-height:130px}.hint{font-size:13px;color:#697b7e;line-height:1.7}.confirmation{display:none;margin-top:20px;padding:22px;border-radius:10px;background:var(--pale)}
@media(max-width:720px){header{align-items:flex-start;flex-direction:column}nav{gap:16px;flex-wrap:wrap}.hero .wrap{padding-top:70px}.cards,.grid{grid-template-columns:1fr}.form{padding:24px}}
"""


def page_shell(name, accent, highlight, pale, content, title):
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(name)}｜{title}｜非公式試作</title><meta name="description" content="{escape(name)}向けの非公式Webサイトデザイン試作です。"><link rel="stylesheet" href="../style.css"><style>:root{{--accent:{accent};--highlight:{highlight};--pale:{pale}}}</style></head><body><div class="notice">非公式のデザイン試作です。事業内容・営業時間などの情報は事業者による確認前です。</div><header><a class="brand" href="index.html"><small>WEB DESIGN CONCEPT</small>{escape(name)}</a><nav><a href="index.html">ホーム</a><a href="index.html#guide">ご案内</a><a href="contact.html">お問い合わせ案</a></nav></header>{content}<footer>{escape(name)} 向け非公式デザイン案｜掲載内容は仮置きです</footer></body></html>'''


def build_demo(number, lead):
    name, area = lead["name"].strip(), lead["area"].strip()
    accent, highlight, pale = PALETTES[number % len(PALETTES)]
    folder = DEMOS / f"{number:02d}"
    folder.mkdir(parents=True, exist_ok=True)
    home = f'''<main><div class="hero"><div class="wrap"><div class="eyebrow">LOCAL SERVICE · DESIGN CONCEPT</div><h1>相談しやすさを、<br>ひと目で伝える。</h1><p>{escape(name)}様のためのWebサイト画面案です。はじめて訪れる方が、案内を見つけ、相談へ進める構成を想定しています。</p><a class="button" href="contact.html">お問い合わせ画面案を見る</a></div></div><section id="guide"><div class="wrap"><span class="number">01 / INFORMATION</span><h2>知りたいことへ、迷わず。</h2><p class="lead">サービス内容や受付方法は、事業者様に確認したうえで掲載する想定です。ここでは情報の見せ方を試作しています。</p><div class="cards"><div class="card"><span class="number">01</span><strong>ご案内</strong><p>取扱内容を一覧で伝える場所。具体的な内容は確認後に掲載します。</p></div><div class="card"><span class="number">02</span><strong>所在地</strong><p>{escape(area)}。詳細なアクセス情報は確認後に追加します。</p></div><div class="card"><span class="number">03</span><strong>お問い合わせ</strong><p>相談したい方が連絡方法を見つけやすい導線を設けます。</p></div></div></div></section><section class="band"><div class="wrap grid"><div><span class="number">02 / CONTACT</span><h2>次の一歩も、<br>分かりやすく。</h2><p class="lead">お問い合わせ画面は表示と入力の動作を確認できる試作です。実際の送信や予約受付にはつながりません。</p><a class="button" href="contact.html">画面案を開く</a></div><div class="panel"><span class="number">DESIGN NOTE</span><h2>{escape(name)}</h2><p>文字の読みやすさ、情報の探しやすさ、スマートフォンでの見やすさを重視した構成案です。</p></div></div></section></main>'''
    contact = f'''<main><section class="band"><div class="wrap"><span class="number">CONTACT / DESIGN CONCEPT</span><h1>お問い合わせ画面案</h1><p class="lead">{escape(name)}様向けに、入力しやすい相談フォームを試作しました。ここで入力した内容は送信されません。</p><form class="form" id="form"><span class="number">FORM PREVIEW</span><h2>ご相談内容</h2><p class="hint">以下はデザイン確認用です。実際の連絡先や受付方法は事業者様の確認後に設定します。</p><label for="customer">お名前</label><input id="customer" autocomplete="name" required><label for="reply">返信先メールアドレス</label><input id="reply" type="email" autocomplete="email" required><label for="message">ご相談内容</label><textarea id="message" required></textarea><p class="hint">送信テストをしても外部には送られません。</p><button class="button" type="submit">確認画面へ進む</button><div class="confirmation" id="confirmation" role="status">入力内容を受け付けたように見せる試作画面です。実際の送信は行っていません。</div></form></div></section></main><script>document.querySelector('#form').addEventListener('submit',event=>{{event.preventDefault();document.querySelector('#confirmation').style.display='block'}})</script>'''
    (folder / "index.html").write_text(page_shell(name, accent, highlight, pale, home, "トップ画面案"), encoding="utf-8")
    (folder / "contact.html").write_text(page_shell(name, accent, highlight, pale, contact, "お問い合わせ画面案"), encoding="utf-8")
    return {"number": number, "name": name, "area": area, "accent": accent,
            "highlight": highlight, "pale": pale}


def build_all(leads, first_number):
    DEMOS.mkdir(exist_ok=True)
    IMAGES.mkdir(exist_ok=True)
    (DEMOS / "style.css").write_text(STYLE, encoding="utf-8")
    metadata = [build_demo(number, lead) for number, lead in enumerate(leads, first_number)]
    links = "".join(
        f'<li><a href="{item["number"]:02d}/index.html">{item["number"]:02d} · {escape(item["name"])}</a></li>'
        for item in metadata
    )
    (DEMOS / "index.html").write_text(
        '<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>42社向け非公式サイト試作</title><style>body{font:17px/1.8 -apple-system,BlinkMacSystemFont,Meiryo,sans-serif;max-width:850px;margin:50px auto;padding:0 24px;color:#183038}li{padding:9px 0;border-bottom:1px solid #e1e8e4}a{color:#15565b}p{color:#657477}</style></head><body>'
        '<h1>42社向け非公式サイト試作</h1><p>掲載情報と問い合わせ画面は確認用です。フォームは実際に送信されません。</p>'
        f'<ol>{links}</ol></body></html>',
        encoding="utf-8",
    )
    path = ROOT / "demo-metadata.json"
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
