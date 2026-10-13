# ImageGen画面案の制作指示

Built-in ImageGenで、各社のトップ画面と予約希望の確認画面を別々に生成した。予約画面は同じ会社のトップ画面を参照画像にして、配色と写真の雰囲気を揃えた。採用した画像は[メール下書き一覧](email-drafts.md)を参照。

## 参考にした同業サイト

- [豊進自動車サービス](https://www.houshin-j.com/)：工場写真、電話・問い合わせへの導線、サービス案内。
- [三ツ矢オートサービス](https://mitsuya-auto.com/)：整備業の案内、問い合わせ導線。
- [大八自動車](https://www.daihati8.co.jp/)：サービス分類、会社情報、連絡先。
- [ヨコヤマ自動車の予約ページ](https://yokoyama-ms.jp/reserve/)：相談内容、希望日時、車両情報、連絡先の項目。

各サイトの一般的な情報設計だけを参考にした。写真、ロゴ、文章、個別のサービス内容は流用していない。会社ごとの実際の設備や提供サービスを確認できないため、生成画像には「非公式の画面案・写真はイメージ」と明記した。

## トップ画面

共通プロンプトの骨子：

> Use case: ui-mockup. Generate a new polished 16:9 landscape Japanese auto service landing-page screenshot proposal for [company], [area]. Design informed by common patterns of real Japanese independent auto repair LPs: clear header with company name and contact CTA, concise navigation, large service-bay hero image, two prominent actions, and three compact information cards directly below the hero. All images are AI-generated conceptual imagery, not actual premises. Exact text: company name, 非公式の画面案・写真はイメージ, [area]で、車の相談を。, 電話で相談, 予約希望を送る, ご相談内容, ご利用の流れ, アクセス. Avoid phone numbers, prices, reviews, credentials, actual logos, competitor imagery, invented service claims, extra readable text, URLs, and browser chrome.

| 会社 | 配色と写真の指示 |
| --- | --- |
| 東運整備株式会社 | navy/orange、整備士が車を点検する工場風景 |
| 豊島小型自動車株式会社 | deep teal/amber、小型車の点検風景 |
| 有限会社協和自動車整備 | charcoal/brick red、セダンの整備風景 |
| 有限会社木村自動車工業 | navy/warm copper、小型バンの整備風景 |
| K-WORKS | graphite/lime green、車体パネルの確認風景 |

## 予約希望の確認画面

各社の採用トップ画面を`referenced_image_paths`に指定した。共通プロンプトの骨子：

> Use case: ui-mockup. Create a new polished Japanese auto repair appointment request confirmation screen mockup, 16:9 landscape, visually coordinated with the attached homepage reference for [company]. Match its palette, type style, spacing, and credible service-workshop photography. Header; 3-step indicator 入力 → 確認 → 完了 with 確認 active; heading 予約希望の確認; sentence 以下の内容をご確認ください。送信後に予約内容を調整します。; confirmation rows 相談内容, 希望日時, 車種・年式, お名前, 電話番号 with dash placeholders; buttons この内容で送信 and 入力に戻る; notices 送信時点で予約は確定しません and 非公式の画面案・写真はイメージ. No invented data, phone numbers, URLs, logos, certifications, reviews, prices, or extra readable text.

画像は画面案であり、フォームは動作しない。
