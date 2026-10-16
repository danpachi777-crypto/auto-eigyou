# local-web-sales

ローカルの提案メール8通を生成・確認し、必要なときだけ送信するコマンドラインツールです。Python標準ライブラリだけで動きます。送信元は全件「デザインダンweb制作担当 中川 <contact.designdan@gmail.com>」、本文の連絡先は`contact.designdan@gmail.com`です。共通設定は[`proposals/sender.py`](../proposals/sender.py)にあります。

## 50通の未送信メール

既存のデモ画像付き8通と、[`leads.csv`](leads.csv)に記録した公開メールアドレス宛ての42通を、[`drafts/`](drafts/)にまとめます。追加42通にも各社名・所在地を反映した[ローカルの非公式サイト試作](demos/index.html)と、トップ画面・お問い合わせ画面の画像2点を用意し、メール本文に埋め込みます。画面案の内容は仮置きで、フォームは実際に送信されません。`leads.csv`には、東京都自動車整備振興会の掲載メールと所在地、サイト確認の記録を残しています。協会一覧のURL欄が空欄で、社名と所在地の検索で独立した公式サイトを確認できなかった候補です。サイトが存在しないことの証明ではありません。

```bash
python3 local-web-sales/fifty.py build
python3 local-web-sales/fifty.py check
```

追加42社の画像は、同業のLPで一般的な構成を調べ、Built-in ImageGenで各社のトップ画面と確認画面を別々に制作しました。確認画面には各社のトップ画面をスタイル参照として使っています。制作方針は[`imagegen-prompts.md`](imagegen-prompts.md)、元画像84点は[`imagegen-originals/`](imagegen-originals/)にあります。`build`はこれらの画像を使って50通の`.eml`、42社のローカル試作、[`drafts/index.csv`](drafts/index.csv)を生成します。以前のSwift描画画像は生成しません。各メールには未送信フラグ`X-Unsent: 1`を付けています。`check`は件数、宛先、差出人、返信先、本文の連絡先、デモ画像2点の埋め込みを検査します。この操作ではメールを送信せず、Gmailの下書きにも登録しません。送信前に宛先の事業実態とサイトの有無を再確認してください。

2026年10月13日、生成した50通を`danpachi777@gmail.com`のGmail下書きに登録しました。送信元は全通`contact.designdan@gmail.com`、画像は各通2点、送信はしていません。[`drafts/gmail-drafts.csv`](drafts/gmail-drafts.csv)に対応する下書きIDを記録しています。Gmail連携への登録は`build`コマンドの動作には含まれません。再登録の際は重複下書きを確認してください。

## 毎日の新規営業メール

[`daily-outreach/PROMPT.md`](daily-outreach/PROMPT.md)の手順で、毎日新規100社を調査し、会社ごとの画面案2点とメールを作成します。Gmail下書きの内容と画像を確認してから送信し、送信済みも確認します。候補の出典、ローカルの`.eml`と画像、Gmail下書きID、送信結果は[`daily-outreach/ledger.csv`](daily-outreach/ledger.csv)に記録します。既存の50社、過去の台帳、Gmail内のメールと重複しない候補を選びます。対象はこの毎日処理で新たに作成したメールのみです。

このMacのLaunchAgent `com.designdan.local-web-sales-daily` が日本時間の毎日午前1:00に [`daily-outreach/run_daily.sh`](daily-outreach/run_daily.sh) を起動します。稼働中の設定ファイルは `/Users/kazu/Library/LaunchAgents/com.designdan.local-web-sales-daily.plist` で、同じ内容を[`daily-outreach/com.designdan.local-web-sales-daily.plist`](daily-outreach/com.designdan.local-web-sales-daily.plist)に保存しています。ローカルのスキルと接続済みGmailを使うため、Macへのログインと実行環境の利用が必要です。処理結果は `daily-outreach/run-report-YYYY-MM-DD.md` に、実行ログは `daily-outreach/runs/` に残します。

リポジトリのルートで実行します。

```bash
python3 local-web-sales/cli.py build
python3 local-web-sales/cli.py check
```

`build`は自動車整備5通と別業種3通の`.eml`を再生成して検査します。`check`は差出人、宛先、本文の名乗りと連絡先、画像2点を検査し、送信先と件名を表示します。`--group auto`または`--group other`で絞り込めます。1通だけなら`--company toun`などを指定します。

アプリパスワードを発行したら、まず送信せずに認証だけ確認できます。

```bash
python3 local-web-sales/cli.py auth
```

認証に成功した場合でも、パスワードは保存されません。実際に送信する際は再入力します。

対象と内容を確認したうえで、送信する場合は次を実行します。

```bash
python3 local-web-sales/cli.py send --company toun
```

送信前に`SEND`と入力し、`contact.designdan@gmail.com`のGoogleアプリパスワードを入力します。5通なら`--group auto`、8通なら`--group all`を指定できます。パスワードは実行時に入力し、ファイルには保存しません。Googleアカウントの通常のログインパスワードは使いません。アプリパスワードは[Googleの案内](https://support.google.com/mail/answer/185833?hl=ja)に従って発行してください。2段階認証が必要で、アカウントの設定によっては発行できません。

ChatGPTのGmail連携、受信メールの同期、既存のGmail下書きは使いません。SMTPが受け付けたメールは取り消せません。複数通の送信が途中で失敗した場合、既に送信済みと表示された宛先に再送しないよう、結果を確認してください。
