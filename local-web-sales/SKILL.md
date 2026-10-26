---
name: local-web-sales
description: Use the local-web-sales project to prepare or revise company-specific website demo images and unsent proposal emails. Applies to requests about this project's leads, demos, .eml files, or Gmail drafts.
---

# local-web-sales

Project: this `local-web-sales` directory in the repository.

Follow `../docs/website-review.md` for multi-source discovery and evidence-based mobile/desktop website review before preparing any new proposal. Prioritize candidates with a verified, actionable improvement; hold unverifiable or no-issue candidates.

Before preparing any new proposal, verify that the business currently has a Google Maps rating of at least 3.0 and at least 10 reviews (inclusive). Apply this to existing candidate lists as well. Record the Google Maps URL, rating, review count, and verification date in research notes. Exclude candidates below either threshold or with unverifiable values; preserve historical research as historical observations.

For a demo image, inspect the lead's actual public information and several current landing pages from the same industry. Use competitors only for general content structure and inquiry flow. Do not copy their text, logos, photos, distinctive layout, or unsupported claims. Keep the demo clearly labelled as unofficial and its photos as illustrative.

Use the built-in ImageGen tool and its `imagegen` skill to create one original 16:9 homepage image per company. Make a separate ImageGen call for that company's inquiry or confirmation image, using the homepage as a style reference. Inspect the outputs for company name, industry fit, readable Japanese, and misleading details. Save final assets in the project. Do not substitute code-drawn browser mockups for ImageGen images. The original eight-company workflow and prompts are recorded in `../proposals/imagegen-prompts.md` and `../proposals/other-industries/imagegen-prompts.md`.

Keep two images embedded in each unsent proposal email. The common sender and contact are `デザインダンweb制作担当 中川 <contact.designdan@gmail.com>`. Build and check local `.eml` with `fifty.py`. When a request includes updating existing Gmail drafts, replace their images in place using the IDs in `drafts/gmail-drafts.csv`, then verify the draft count and embedded images. Never send a message unless the user explicitly asks to send it.

Use this Japanese email copy as the baseline, adapting the service and second image label to each company. Keep the sender display name above, but use only `中川` and `contact.designdan@gmail.com` in the signature. Do not mention using other companies' site structures, company approval or supervision, or sample form behavior in the email.

> 件名：{会社名}様向けWebサイト画面案のご提案
>
> {会社名} ご担当者様
>
> 突然のご連絡失礼いたします。フリーランスでweb制作をしている中川と申します。
>
> 御社のWebサイトを拝見し、{確認した改善点1つの事実}を確認しました。
>
> {その1点をどう改善するか}という改善を考え、公開情報をもとに{会社名}様向けの画面案を作成しました。トップ画面と{第2画面}の画像を、このメールに掲載しています。
>
> 今回は上記の改善に範囲を絞ったご提案です。対応範囲は現在のサイトの仕様を伺ったうえで確認します。
> 費用目安：{ユーザーが確定した料金・税込／税別・適用範囲。未確定なら仕様確認後に個別案内}
> 納期目安：{ユーザーが確定した納期・起算条件。未確定なら仕様確認後に個別案内}
>
> この部分の見直しは、現在ご検討されていますか？
>
> ※画像は非公式のデザイン案です。写真はイメージで、実際の店舗・設備を示すものではありません。
>
> 中川  
> contact.designdan@gmail.com


2026-10-20更新：初回は根拠のある改善点を1つだけ取り上げ、その改善が画像2点にも分かるようにする。会議予約リンクや面談日時の要求を初回の質問に追加しない。既存文面の「少しでもご関心がありましたら」は使わず、答えやすい関心確認の質問を1つ置く。料金・納期・対応範囲は `daily-outreach/offer.json` のユーザー確定情報だけを使い、架空の実績・成果保証・価格・日数を作らない。`build_one.py` に `--website-review <調査JSON>` と必要なら `--finding-index` を渡す。

再連絡は基本なし。未返信先への追客・リマインド・別アドレスへの再提案を自動で行わない。既送信の10件も追客しない。受信した返信は未返信への追客とは区別し、別途の指示に従って対応する。業種別の効果比較は今後の実データが蓄積してから行い、現時点でアポ率向上や勝ち業種を確認済みとはしない。
