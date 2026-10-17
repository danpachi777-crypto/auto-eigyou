# Outreach run — 2026-10-17

## Result

- Target: 100 verified sent emails to new companies.
- Verified sent from this run: **5**.
- Shortfall: **95**.
- Remaining Gmail drafts from this run: **0** (Gmail draft list was empty at final audit).
- Connected Gmail account: `danpachi777@gmail.com`.
- Sending used only the five newly created and read-back-verified drafts listed below. No older draft was sent.

Each candidate was checked against normalized company names and email addresses in `leads.csv`, `drafts/index.csv`, and `daily-outreach/ledger.csv`, plus Gmail all-mail, Drafts, and Sent searches. Each message was built with the Japanese baseline, two separate built-in ImageGen images, plain text and HTML, and the nonofficial-image disclosure. `fifty.py check-daily` passed for each EML. The draft was read back before the ledger row was appended; Sent was searched again immediately before sending. Each returned sent message was read back and checked for `SENT`, recipient, subject, and two nonempty inline JPEGs referenced by CID. The ledger was updated only after that verification.

| Company | Industry / region | Published business email and source | Activity evidence | Sent message ID | Sent at (JST) |
| --- | --- | --- | --- | --- | --- |
| ミパウンドトーキョー | パウンドケーキ製造・販売 / 東京都葛飾区 | `contact@mipoundtokyo.com` — https://mipoundtokyo.com/ | Official site lists an October 15, 2026 event notice and September 30 sales resumption. | `1a1458923c7c171f` | 2026-10-17 01:26:17 |
| Atelier Toco | 花店・フラワーレッスン / 大阪市北区 | `info@atelier-toco.com` — https://atelier-toco.com/ | Official site lists an October 2026 business calendar and flower services. | `1a1458bad7b48678` | 2026-10-17 01:29:03 |
| 有限会社 北陸製本センター（製本工房） | 製本・紙加工 / 福井市 | `kasakawa.hokurikuseihon@gmail.com` — https://www.hokuriku-b.jp/category/news/ (published as the contact during email app trouble) | Official site lists an August 6, 2026 holiday notice and August 17 return to regular operations. | `1a1458e4051b5bfd` | 2026-10-17 01:31:53 |
| AMOLIR | 靴修理 / 東京都小金井市 | `info@amolir501.com` — https://amolir501.com/ | Official homepage lists October 2026 business notices; an older notice says bag repair ceased, so the proposal covers shoe repair only. | `1a145913738be54f` | 2026-10-17 01:35:06 |
| 茶舗 ゆと葉 | 日本茶販売 / 京都府宇治市 | `info@chaho-yutoha.com` — https://chaho-yutoha.com/policies/legal-notice | Official homepage lists a September 10, 2026 update and current tea products. | `1a1459421216183b` | 2026-10-17 01:38:17 |

The matching draft IDs were `r8042224106773162930`, `r6436919163478345556`, `r8895022758400041457`, `r-4814480147706097429`, and `r6677514273294537449`. The local EML and image paths, source URLs, check dates, statuses, sent IDs, and timestamps are in [ledger.csv](ledger.csv). Assets are in `assets/2026-10-17/<company-slug>/`; EMLs are in `eml/2026-10-17/`.

## Design research

- Pound cake: https://www.coconopound.jp/, https://www.youandg.co.jp/, https://www.pavlov.jp/shop/.
- Florist: https://uto-flower.com/, https://www.green-ya.com/, https://www.hanapokapoka.com/.
- Bookbinding: https://www.i-booklet.com/, https://www.book-hon.com/, https://www.kobayashiseihon.jp/orderflow/.
- Shoe repair: https://www.sankidoo.com/, https://www.aprestocare.com/, https://resh.tv/shop/.
- Japanese tea: https://chairie.jp/, https://shop.kouroan.com/, https://www.fujiya-chaho.com/.

These pages informed only general service presentation and inquiry flow. The generated images use illustrative scenes and visible `非公式デザイン案` labels. The homepage and inquiry image for each business were visually checked for readable names and Japanese, industry fit, and misleading details. The tea homepage was revised with a further built-in ImageGen call to remove scenery that might be mistaken for a real shop location.

Built-in ImageGen prompt set, summarized: (1) ミパウンドトーキョー: warm cream and cocoa pound-cake homepage, then matching blank inquiry page; (2) Atelier Toco: sage and olive flower-service homepage, then matching blank inquiry page; (3) 製本工房: navy and copper paper-craft service homepage, then matching blank estimate inquiry page; (4) AMOLIR: charcoal and saddle-tan shoe-repair homepage, then matching blank inquiry page, excluding discontinued bag repair; (5) 茶舗 ゆと葉: matcha-green tea-selection homepage, revised to remove recognizable scenery, then matching blank inquiry page. Each second image used its final homepage as a style reference. All prompts required the exact business name, readable Japanese, a visible unofficial label, generic illustrative photos, and no unverified prices, claims, addresses, or contact details. The complete tool prompts are also recorded in the dated run log `runs/2026-10-17.jsonl`.

## Skipped candidates

- 陶芸教室の新陶房: official page says classes ended in May 2026; excluded due to inactive service (https://www.shintoubou.com/%E9%99%B6%E8%8A%B8%E6%95%99%E5%AE%A4/).
- flower est: the page displays conflicting spellings of the email address; excluded because the contact could not be confirmed confidently (https://floweresta.com/archives/news).
- ガラス工房Kirlo: search result displays a likely site-template address alongside a different address; excluded because the published contact was ambiguous (https://eijiglass.wixsite.com/kirlo/blank-3).

## Remaining work and constraint

The required research, two separate built-in ImageGen calls, image inspection, local EML validation, Gmail draft readback, Sent duplicate check, sending, and Sent readback must occur sequentially for each company. This run completed five full cycles. **95 valid, individually prepared and verified sends remain**. No lead, image, draft, or sent status has been fabricated for the shortfall.
