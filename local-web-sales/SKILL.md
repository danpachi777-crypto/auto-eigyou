---
name: local-web-sales
description: Use the local-web-sales project to prepare or revise company-specific website demo images and unsent proposal emails. Applies to requests about this project's leads, demos, .eml files, or Gmail drafts.
---

# local-web-sales

Project: this `local-web-sales` directory in the repository.

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
> {地域}で{サービス}を探している方に、事業内容や相談方法が分かりやすく伝わるWebサイトを考え、公開情報をもとに{会社名}様向けの画面案を作成しました。トップ画面と{第2画面}の画像を、このメールに掲載しています。
>
> 画面案をご覧いただき、少しでもご関心がありましたら、掲載したい内容を伺ったうえで、必要なページや制作範囲、概算費用をご案内します。ご返信いただければ幸いです。
>
> ※画像は非公式のデザイン案です。写真はイメージで、実際の店舗・設備を示すものではありません。
>
> 中川  
> contact.designdan@gmail.com
