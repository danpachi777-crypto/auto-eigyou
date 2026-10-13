# 異業種3件の非公式メール下書き

調査・作成日: 2026年10月13日

自動車整備以外の3業種について、Googleマップの店舗データでWebサイト欄が空欄であること、社名と所在地で独立した公式サイトを見つけられないこと、公開メールアドレスが店舗名と所在地に結び付くことを確認した。結果は[候補一覧](../../data/companies_other_industries.csv)に記録した。「サイトが存在しない」との断定ではない。Googleマップの掲載情報は変わり得る。

| 業種・事業者 | 出典 | トップ画面 | 確認画面 | ローカルメール |
| --- | --- | --- | --- | --- |
| 便利屋・ハウスクリーニング：くらしのレスキュー 151a | [Googleマップ](https://www.google.com/maps/place/?q=place_id:ChIJbwiuMm6JGGARTikS_3veCtQ)・[公開メール](https://www.ekiten.jp/shop_28599644/menu/) | [画像](demos/rescue151a-home-imagegen.png) | [画像](demos/rescue151a-form-imagegen.png) | [EML](rescue151a-email.eml) |
| 仕立屋：テーラードイ | [Googleマップ](https://www.google.com/maps/place/?q=place_id:ChIJATXhfundAGARmVqINnPqGkc)・[公開メール](https://www.ekiten.jp/shop_680932/) | [画像](demos/tailor_doi-home-imagegen.png) | [画像](demos/tailor_doi-form-imagegen.png) | [EML](tailor_doi-email.eml) |
| 理容店：ヘアーファクトリーＪＵＮ | [Googleマップ](https://www.google.com/maps/place/?q=place_id:ChIJ37WjkPv0QDURy2kKgdAQrKg)・[公開メール](https://www.ekiten.jp/shop_4040886/) | [画像](demos/hair_jun-home-imagegen.png) | [画像](demos/hair_jun-form-imagegen.png) | [EML](hair_jun-email.eml) |

業種のLP構成は[ハウスクリーニング東京](https://housecleaning-tokyo.co.jp/)、[サトウテーラー](https://www.satotailor.com/)、[Bar Ber Gnarly styles](https://www.gnarly.jp/)などの実在サイトを参考にした。写真、文章、ロゴ、価格は流用していない。生成画像は実際の店舗・設備を示さない画面案で、確認フォームは動作しない。採用した制作指示は[imagegen-prompts.md](imagegen-prompts.md)に記録した。

Gmail下書きは3件とも未送信。下書きIDは順に`r-8676096540701096442`、`r-6165459089974291315`、`r619583392633657938`。本文にデモサイトURLを入れず、トップ画面と確認画面の画像を本文内に埋め込んだ。ローカルの`.eml`は、差出人を「デザインダンweb制作担当 中川 <contact.designdan@gmail.com>」、本文の連絡先を`contact.designdan@gmail.com`に統一した。`danpachi777@gmail.com`側のGmail下書きも差出人と返信先を`contact.designdan@gmail.com`に更新し、Gmailで同アドレスの送信確認を完了した。原稿の再生成と確認は[`local-web-sales`](../../local-web-sales/README.md)から行える。
