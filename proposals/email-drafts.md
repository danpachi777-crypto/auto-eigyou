# 5社向けメール下書き

作成日: 2026年10月13日

各社のGmail下書きとローカルの`.eml`には、同業の整備会社サイトの構成を参考にImageGenで制作したトップ画面案と予約希望の確認フォーム案を本文内に掲載しています。メール本文にデモサイトのURLはありません。画像は非公式のデザイン案で、車・背景は実際の店舗や設備を示すものではありません。フォームは動作しません。送信は行っていません。

| 会社 | メール下書き | トップ画面案 | フォーム案 |
| --- | --- | --- | --- |
| 東運整備株式会社 | [`toun-seibi-email.eml`](toun-seibi-email.eml) | [`toun-home-imagegen-v3.png`](demos/toun-home-imagegen-v3.png) | [`toun-form-imagegen-v5.png`](demos/toun-form-imagegen-v5.png) |
| 豊島小型自動車株式会社 | [`toshima-email.eml`](toshima-email.eml) | [`toshima-home-imagegen-v3.png`](demos/toshima-home-imagegen-v3.png) | [`toshima-form-imagegen-v3.png`](demos/toshima-form-imagegen-v3.png) |
| 有限会社協和自動車整備 | [`kyowa-email.eml`](kyowa-email.eml) | [`kyowa-home-imagegen-v3.png`](demos/kyowa-home-imagegen-v3.png) | [`kyowa-form-imagegen-v3.png`](demos/kyowa-form-imagegen-v3.png) |
| 有限会社木村自動車工業 | [`kimura-email.eml`](kimura-email.eml) | [`kimura-home-imagegen-v3.png`](demos/kimura-home-imagegen-v3.png) | [`kimura-form-imagegen-v3.png`](demos/kimura-form-imagegen-v3.png) |
| K-WORKS | [`kworks-email.eml`](kworks-email.eml) | [`kworks-home-imagegen-v3.png`](demos/kworks-home-imagegen-v3.png) | [`kworks-form-imagegen-v3.png`](demos/kworks-form-imagegen-v3.png) |

ローカルの5通は、差出人を「デザインダンweb制作担当 中川 <contact.designdan@gmail.com>」、本文の連絡先を`contact.designdan@gmail.com`に統一しています。`danpachi777@gmail.com`側のGmail下書きも、差出人・返信先を`contact.designdan@gmail.com`に更新しています。Gmailで同アドレスの送信確認を完了し、既定の差出人にも設定しました。メール用の軽量画像は[`email-images/`](email-images/)にあります。

## Gmail連携を使わずに送る場合

[`local-web-sales`](../local-web-sales/README.md)は`contact.designdan@gmail.com`のGmail SMTPで送信します。ChatGPTのGmail連携や受信メールの同期は使いません。送信には、そのGoogleアカウントで2段階認証を有効にして発行した**アプリパスワード**が必要です。通常のGoogleログインパスワードは入力しないでください。アプリパスワードは実行時に入力し、ファイルには保存しません。

まず宛先・件名を確認します。この操作では送信しません。

```bash
python3 local-web-sales/cli.py check --group auto
```

内容を確認した後に送信する場合は`send`コマンドを使います。まず1社ずつ送るなら、`--company toun`（ほかは`toshima`、`kyowa`、`kimura`、`kworks`）を指定します。

```bash
python3 local-web-sales/cli.py send --company toun
```

実行時に`SEND`と入力し、アプリパスワードで認証した後に送信されます。送信結果はSMTPが受け付けた宛先ごとに表示されます。
