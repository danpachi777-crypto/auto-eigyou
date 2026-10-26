"""Verify single-issue proposals and truthful commercial terms without sending."""
import json
import struct
import tempfile
import unittest
import zlib
from contextlib import redirect_stdout
from email import policy
from email.parser import BytesParser
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import build_one


class ProposalCopyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.review_path = self.root / "review.json"
        self.offer_path = self.root / "offer.json"
        self.review = {"company": "テスト商店", "priority": "medium", "findings": [
            {"url": "https://example.com/contact", "observation": "390px幅で案内文字が重なっている。",
             "proposal": "問い合わせ案内の文字を重ならずに表示する"},
            {"url": "https://example.com/menu", "observation": "別の指摘。", "proposal": "別の改善"}]}
        self.offer = {"price_confirmed": False, "price_text": "未承認の999円",
                      "turnaround_confirmed": False, "turnaround_text": "未承認の即日",
                      "scope_confirmed": False, "allowed_scope": "未承認の全機能"}
        self.args = SimpleNamespace(company="テスト商店", website_review=str(self.review_path),
                                    finding_index=0, second_label="お問い合わせ画面")
        self.save()
        self.patcher = patch.object(build_one, "OFFER", self.offer_path)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def save(self):
        self.review_path.write_text(json.dumps(self.review, ensure_ascii=False))
        self.offer_path.write_text(json.dumps(self.offer, ensure_ascii=False))

    def test_one_finding_and_no_unapproved_terms(self):
        copy = "\n".join(build_one.proposal_copy(self.args))
        self.assertIn(self.review["findings"][0]["observation"], copy)
        self.assertNotIn("別の指摘", copy)
        self.assertNotIn("未承認", copy)
        self.assertIn("仕様を確認後", copy)
        self.assertEqual(copy.count("？"), 1)
        self.assertNotIn("打ち合わせ", copy)

    def test_confirmed_terms_are_preserved_exactly(self):
        self.offer.update(price_confirmed=True, price_text="10万円（税込）、1ページの制作",
                          turnaround_confirmed=True, turnaround_text="素材確定から3週間目安",
                          scope_confirmed=True, allowed_scope="1ページのデザイン・実装")
        self.save()
        copy = "\n".join(build_one.proposal_copy(self.args))
        for key in ("price_text", "turnaround_text", "allowed_scope"):
            self.assertIn(self.offer[key], copy)

    def test_hold_and_wrong_company_are_blocked(self):
        for change in ({"priority": "hold"}, {"company": "別会社"}):
            with self.subTest(change=change):
                prior = self.review.copy()
                self.review.update(change)
                self.save()
                with self.assertRaises(ValueError):
                    build_one.proposal_copy(self.args)
                self.review = prior

    def test_missing_evidence_and_missing_confirmed_term_are_blocked(self):
        self.review["findings"][0]["observation"] = ""
        self.save()
        with self.assertRaises(ValueError):
            build_one.proposal_copy(self.args)
        self.args.finding_index = 1
        self.offer.update(price_confirmed=True, price_text=None)
        self.save()
        with self.assertRaises(ValueError):
            build_one.proposal_copy(self.args)

    def test_mime_contains_same_proposal_and_two_inline_images(self):
        # A tiny synthetic PNG fixture exercises encoding, not user artwork generation.
        def chunk(tag, data):
            return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))
        png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 160, 90, 8, 2, 0, 0, 0))
               + chunk(b"IDAT", zlib.compress((b"\x00" + b"\x80\x80\x80" * 160) * 90)) + chunk(b"IEND", b""))
        source = self.root / "fixture.png"
        source.write_bytes(png)
        self.args.__dict__.update(date="test", slug="fixture", region="テスト地域", service="テスト業種",
                                  email="test@example.com", home=str(source), inquiry=str(source))
        with patch.object(build_one, "ROOT", self.root), redirect_stdout(StringIO()):
            build_one.build(self.args)
        message = BytesParser(policy=policy.default).parsebytes((self.root / "eml/test/fixture.eml").read_bytes())
        bodies = {p.get_content_type(): p.get_content() for p in message.walk()
                  if p.get_content_type() in ("text/plain", "text/html")}
        for body in bodies.values():
            self.assertIn(self.review["findings"][0]["observation"], body)
            self.assertIn("この部分の見直しは、現在ご検討されていますか？", body)
            self.assertNotIn("未承認", body)
        images = [p for p in message.walk() if p.get_content_type() == "image/jpeg"]
        self.assertEqual(len(images), 2)
        for image in images:
            self.assertTrue(image.get_payload(decode=True))
            self.assertEqual(image.get_content_disposition(), "inline")
            self.assertIn("cid:" + image["Content-ID"].strip("<>"), bodies["text/html"])


if __name__ == "__main__":
    unittest.main()
