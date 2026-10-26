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

## 現在の実行方法（2026年10月20日更新）

ユーザーの指示により毎晩21時のLaunchAgentを解除しました。現在は、このリポジトリのCodexで `kz` と指示したときだけ開始・再開します。`kz status` は状況確認だけです。会話が終了すると手動処理は停止します。新しい明示的な依頼なしに定期実行を再登録しないでください。

### 旧・夜間自動実行の参考資料（現在は無効）

全国のGoogleマップで**評価3.0以上・口コミ10件以上**の事業者を対象にします。新規・既存の候補を問わず、公開メール、営業実態、評価・口コミ件数を確認し、出典と確認日を記録します。過去のリストだけで条件適合とはみなしません。

macOSのLaunchAgentが毎晩21:00（日本時間）に`daily-outreach/nightly.py`を起動します。`NIGHTLY.md`に従い、Codex CLIが候補調査、ImageGenによる会社別画像2点の制作、メール作成、Gmail下書き検証、送信、送信済み読み戻しまで1社ずつ自動処理します。`kz`の入力は不要です。CodexのログインとGmail連携が必要で、Macは電源・ネット接続があり、スリープしない状態にしてください。Mac停止中のクラウド実行には対応していません。

上限は**日本時間の1日450件かつ直近24時間450件**です。複数キャンペーンの実績を合算し、直前にGmailの送信済み全ページを確認します。送信前にSQLiteへ予約し、送信済み確認後に確定します。未確定の予約がある場合は停止して照合を要求します。二重起動はロックで防ぎます。通常のメールもGmail側の上限に含まれます。

処理時間帯は21:00〜翌09:00の最大12時間、1社は最大30分です。スリープ等で起動が遅れた場合、日中の送信は開始しません。候補不足、画像生成・Gmailの利用制限、認証エラー、送信結果の不明、確認済み送信が増えない場合は停止し、理由を記録します。450件は上限・目標であり、毎晩の達成を保証しません。必要なツールが夜間のCLIで使えない場合も送信せず停止します。

```bash
# 実送信をしない起動設定確認
python3 local-web-sales/daily-outreach/nightly.py --dry-run
# 夜間CLIでのGmail接続と必要ツールを確認（送信・下書き作成なし）
python3 local-web-sales/daily-outreach/nightly.py --preflight
# スケジュールのインストール（直ちに実行はしない）
python3 local-web-sales/daily-outreach/schedule.py install
# 登録状況、件数と未確定予約の確認
python3 local-web-sales/daily-outreach/schedule.py status
python3 local-web-sales/daily-outreach/delivery_budget.py status
# 自動実行の停止
python3 local-web-sales/daily-outreach/schedule.py uninstall
```

実行ログ・結果・送信枠のDBは`daily-outreach/runs/`に保存し、Gitには含めません。`ledger.csv`は既存の列・行を保持します。DBや台帳を削除して上限をリセットしないでください。以前のSMTPツールは日次管理と統合されていないため、自動キャンペーンとの併用はしません。

`kz`は手動の開始・再開用として残しています。手動でも共通の450件制限と送信前予約を適用し、夜間実行中は送信しません。`manual_campaign.py`は状態管理のみで、それ自体は送信しません。

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
