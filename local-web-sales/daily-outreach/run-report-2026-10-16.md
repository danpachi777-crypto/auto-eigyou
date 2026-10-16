# Outreach run — 2026-10-16

## Final status and Gmail audit at 13:43 JST

The earlier completion claim below is no longer current. The connected account was confirmed as `danpachi777@gmail.com`. Gmail `list_drafts` and `in:drafts` both returned **0 drafts**. All ten companies in today's ledger appeared in `in:sent` with the same proposal subjects and two inline images, timestamped 13:37:07–13:37:29 JST. The ledger's `r...` draft IDs no longer identify readable Gmail messages; their status must not be treated as proof of an unsent draft.

The local run log records `gmail.create_draft`, `gmail.read_email`, `gmail.list_drafts`, `gmail.search_emails`, and `gmail.get_profile` calls, with no `gmail.send_draft` or `gmail.send_email` call found. The user confirmed that they personally sent the ten messages.

The user set today's cap at **10**. Ten distinct drafts were created and verified earlier today; no additional drafts were created when the 20-per-day run was started. At this audit, **0 remain as drafts and all 10 appear in Sent**. The ten recipients have already been contacted and are excluded from any retry. The present audit performed no send operation. Additional draft creation was stopped for today.

Sent message IDs observed: `1a14300371cf95ed`, `1a143003007abb3d`, `1a1430029c83a24b`, `1a14300232eea3dd`, `1a143001cb545979`, `1a1430011bb35b2d`, `1a143000bd94dc74`, `1a14300047bd76b3`, `1a142ffe941e17ea`, `1a142ffe1632611d`.

The candidate screening notes and local artifacts below are retained as historical records; their prior draft verification describes the earlier account state.

- Target for today: 10 new Gmail drafts
- Created and verified earlier today: 10
- Current Gmail drafts among those 10: 0
- Current Gmail Sent among those 10: 10
- Connected account: `danpachi777@gmail.com`
- Draft IDs: see the ledger and continuation table below
- Additional drafts after the user capped today at 10: 0

## Selected lead

| Field | Value |
| --- | --- |
| Company | 寺見たたみ店 |
| Industry | 畳製造・畳店 |
| Region | 岡山市北区 |
| Published business email | `info@terami-tatami.jp` |
| Email and business source | https://terami-tatami.jp/ |
| Website | https://terami-tatami.jp/ |
| Checked | 2026-10-16 |

The business's own homepage lists the email, industry, and 岡山市北区 location. Its 2026-09-22 campaign notice and 2026-09-01 payment update support current activity. The same site describes 新畳、表替え、裏返し and inquiry options. Its website is acknowledged as existing; the proposal does not say it lacks one.

Duplicate checks used normalized company and email against `leads.csv`, `drafts/index.csv`, the daily ledger, and Gmail searches across all mail; no match was found. Gmail had no preexisting drafts at the start of this run. The new draft was listed once after creation.

## Design research and assets

Several current 畳店 landing pages were inspected for general service explanation and inquiry structure: https://kitagawatatamiten.com/, https://www.m-kitazawatatami.com/, and https://www.tatamino-ouchi.com/. Their text, photos, logos, and distinctive designs were not copied.

Two separate built-in ImageGen calls produced the original homepage and an inquiry screen, with the homepage used as a style reference for the second call. Both were visually inspected for exact business name, readable Japanese, industry fit, and a visible `非公式デザイン案` label. Photographic scenes are illustrative, not the actual shop. The generated 1672 × 941 images were saved as JPEGs for email:

- `assets/2026-10-16/terami-tatami/home.jpg`
- `assets/2026-10-16/terami-tatami/inquiry.jpg`

Homepage prompt: an original, spacious Japanese 畳店 desktop homepage in ivory, indigo, and sage, showing only verified business name, location, 新畳・表替え・裏返し, inquiry navigation, illustrative tatami imagery, and a nonofficial label; no prices, claims, people, or contact details.

Inquiry prompt: a separate matching page using the homepage as style reference, with empty name, email, and consultation fields and a conceptual confirmation button, plus the same nonofficial label; no invented details or submission success.

## Email and Gmail verification

- Local EML: `eml/2026-10-16/terami-tatami.eml`
- `python3 local-web-sales/fifty.py check-daily --path local-web-sales/daily-outreach/eml/2026-10-16/terami-tatami.eml --to info@terami-tatami.jp` passed.
- Gmail creation returned draft ID `r-5774604190298543010`.
- Gmail readback initially confirmed the `DRAFT` label, recipient, subject, plain-text and HTML bodies, nonofficial disclosure, and two nonempty inline JPEGs with matching `cid:terami-home` and `cid:terami-inquiry` references. It later appeared in Sent, as noted above.
- Ledger row was appended only after this readback passed.

## Skipped candidates

- クリスター — an older official site says new orders are stopped, creating uncertainty despite a newer site and directory listing: https://www.clestar.jp/ and https://kristar.jp/.
- クリーンスター — its current site shows an inquiry form but no published email address on the checked pages: https://clean-star-pikapika.com/company/.
- REVIVE SERVICE — public email exists, but the visible updates were from 2019; current operation could not be established confidently: https://www.revive-service.jp/.
- ホリウチ畳店 — the current homepage shows 2026 work, but a search result's older email and address did not match the current pages; skipped the uncertain contact: https://www.horiuchitatami-kiwami.com/.
- 三谷商店 — 2026 activity was visible, but no published email was found: https://mitanishouten.jp/.

Blockers: none.

## Continuation to 10 drafts

Nine additional, distinct businesses were researched and completed on 2026-10-16: four more tatami businesses and five businesses in other industries. Each had a published business email, current activity evidence, company and email normalization checks against the three local lists and Gmail all-mail search, two separate built-in ImageGen calls, visual inspection, `fifty.py check-daily`, Gmail creation and message readback. The readback confirmed `DRAFT`, recipient, subject, plain and HTML bodies, the nonofficial disclosure, and two nonempty inline JPEG parts with matching CID references. Ledger rows were appended after readback.

| Tatami business | Region | Published email source | Gmail draft ID |
| --- | --- | --- | --- |
| 小川畳店 | 東京都足立区 | [Official company page](https://ogawatatami.com/aboutus) | `r-530519944947604891` |
| 株式会社天王製畳 | 浜松市中央区 | [Official contact page](https://tennou-tatami.jp/contact/) | `r5932279140794570301` |
| 佐野畳屋 | 福岡県田川市 | [Official contact page](https://sano-tatamiya-fukuoka.co.jp/contact/) | `r3065216455046456564` |
| 白澤畳店 | 東京都練馬区 | [Official contact page](https://www.shirasawa-tatami.co.jp/information/contact/) | `r-1179740656998293523` |

| Company | Industry / region | Published email source and current activity | Same-industry landing pages inspected | Gmail draft ID |
| --- | --- | --- | --- | --- |
| 靴修理店Gato | 靴修理 / さいたま市浦和区 | [Official blog](https://ameblo.jp/gatokutushuri/) lists `repair.gato@gmail.com`, location and October 2026 repair entries. | [RENNON](https://www.rennon.me/contact-us/), [RESH](https://resh.tv/shop/), [MISTER MINIT](https://www.minit.co.jp/service/shoe_repair/) | `r9191375154599473896` |
| 花屋 小梅 | 花店 / 東京都足立区 | [Official shop information](https://hanayakoume.com/about) lists `info@hanayakoume.com`; [homepage](https://hanayakoume.com/) has 2026 news and current store details. | [YASAciHANA](https://yasacihana.com/school/), [Room.coco](https://roomcoco.jp/shop/42/), [新東京花店](https://www.st-flower.com/about.html) | `r-5630576137569696205` |
| レジャーハウスミヤザキ | 自転車販売・修理 / 東京都八王子市 | [Official legal notice](https://miyazaki-bikes.com/policies/legal-notice) lists `info@miyazaki-bikes.com`; [homepage](https://miyazaki-bikes.com/) has October 2026 posts. | [平野自転車商店](https://hirano-cycle.com/), [町のじてんしゃ修理屋さん](https://machijite.com/), [ちいさな自転車家](https://chi-cycle.jp/news/) | `r-4761145090344053563` |
| まだん陶房 | 陶芸教室 / 東京都世田谷区 | [Official July 2026 notice](https://www.madantobo.com/news/%E5%A4%8F%E4%BC%91%E3%81%BF%E9%99%B6%E8%8A%B8%E4%BD%93%E9%A8%93%E3%82%AD%E3%83%A3%E3%83%B3%E3%83%9A%E3%83%BC%E3%83%B3%EF%BC%81/) lists `info@madantobo.com`; [homepage](https://www.madantobo.com/) describes ongoing classes. | [やわら木](https://www.yawara-gi.com/information/), [Cactus](https://potterycactus.com/contact/), [祖師谷陶房](https://www.soshigayatohboh.co.jp/%E4%BE%A1%E6%A0%BC%E6%94%B9%E5%AE%9A%E3%81%AE%E3%81%8A%E7%9F%A5%E3%82%89%E3%81%9B/) | `r-5775349013782812586` |
| 鵜殿製菓 | カステラ製造・販売 / 京都市上京区 | [Official site](https://udono-kyoto.com/) lists `info@udono-kyoto.com`, business location, products and a March 2026 notice. | [三源庵](https://www.sangenan.co.jp/), [カステラのさかえ屋](https://kasutera.net/), [小田藤](https://www.odafuji.com/) | `r-5788682095964045986` |

All new images are in `assets/2026-10-16/<company-slug>/home.jpg` and `inquiry.jpg`; all new messages are in `eml/2026-10-16/<company-slug>.eml`. The [ledger](ledger.csv) records exact paths, source URLs, check dates, and historical draft IDs. The earlier Gmail draft list contained exactly 10 IDs, matching the ten unique ledger rows. The later audit found all ten in Sent, and the user confirmed that they sent them.

### Additional skipped candidates

- こなkona工房 — `kona-pan@konakona.cc` was published as a reservation reply sender, but the checked contact page did not publish it as an inbound business contact: https://konakona.cc/contact.
- ほしのベーカリー — the checked site had no dated 2026 business update; current operation was less clear than the selected candidate: https://hoshino1054.com/.

Today's draft creation count was 10 of 10. The user confirmed that they sent the ten messages.
