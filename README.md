# auto-eigyou

国内事業者の調査記録と、東運整備株式会社を題材にした**非公式ウェブサイト試作**のソースです。

## 内容

- [`data/companies.csv`](data/companies.csv): Googleマップの評価4.0以上・口コミ3件以上で、マップにWebサイトが登録されていなかった事業者30件。調査日とGoogleマップへのリンク付き。
- [`data/companies_with_email.csv`](data/companies_with_email.csv): 上記の候補から公開メールアドレスを別の出典で確認し、公式サイトを再検索した5件。100件の条件を満たすリストではありません。
- [`docs/research-method.md`](docs/research-method.md): 調査条件と「公式サイトなし」という判定の限界。
- [`docs/toun-seibi-sources.md`](docs/toun-seibi-sources.md): 東運整備のサイトに掲載した情報と出典。
- [`site/`](site/): 予約希望フォームと所有者用予約管理画面を含むサイトのソース。
- [`proposals/email-drafts.md`](proposals/email-drafts.md): 公開メールアドレスを確認した5社向けの提案メール草案。
- [`proposals/demos/`](proposals/demos/): 5社それぞれの非公式・静的なサイト試作。公開前のローカル閲覧用です。
- [`proposals/other-industries/`](proposals/other-industries/): 自動車整備以外の3業種向けImageGen画面案と未送信メール下書き。
- [`local-web-sales/`](local-web-sales/): 既存8通の生成・検査・SMTP送信と、追加42通を含む計50通の未送信`.eml`を作成するローカルツール。
- [`data/companies_other_industries.csv`](data/companies_other_industries.csv): 異業種3件のGoogleマップ・公開メール・サイト有無の調査記録。

## 試作サイト

- サイト: https://toun-seibi-demo.otoko777dan.chatgpt.site
- 予約希望: https://toun-seibi-demo.otoko777dan.chatgpt.site/reserve
- 所有者用管理: https://toun-seibi-demo.otoko777dan.chatgpt.site/admin

サイトは非公開の試作です。東運整備株式会社の承認・監修を受けたものではありません。フォーム送信は試作サイト内のデータベースに保存されますが、東運整備への通知や予約手配は行いません。予約は送信時点では確定せず、空き枠の自動照合も行いません。

## 構成と動作

Cloudflare Worker互換のES ModuleをSitesで稼働させ、予約希望はD1の`reservations`テーブルに保存します。管理画面と管理APIは、Sitesが付与する認証済みユーザー情報とホスト環境変数`ADMIN_EMAIL`で所有者を照合します。`ADMIN_EMAIL`の値はリポジトリには含めていません。

サイトのソースは`site/web/`、APIとルーティングは`site/worker/`、データベース定義は`site/drizzle/`にあります。生成物の`dist/`、予約データ、認証情報は保存していません。

ローカルで構文とAPIテストを行う場合:

```sh
cd site
node scripts/build.mjs
node --test tests/booking.test.mjs
node --check dist/server/index.js
```

## 調査データの注意

評価・口コミ数・営業時間などは変動します。`companies.csv`は2026年10月13日時点の調査記録です。「公式サイトなし」の断定ではなく、当時のGoogleマップ掲載欄にURLがなく、社名・所在地での検索でも独立した公式サイトを確認できなかった候補を示します。ただし再検索で、少なくとも「㈱小林自動車」（板橋区宮本町）と「カケン自動車㈱」（葛飾区立石）には独立した公式サイトが見つかりました。`companies.csv`をそのまま条件適合リストとして扱わないでください。営業や公開利用の前に再確認してください。
