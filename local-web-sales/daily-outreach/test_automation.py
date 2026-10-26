"""Delivery limits and interrupted-send behavior, without any network or real mail."""

import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import delivery_budget as budget
import nightly
import schedule


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ledger = self.root / "ledger.csv"
        self.write_ledger([])
        self.db = budget.connect(self.root / "budget.sqlite3")
        self.addCleanup(self.db.close)
        self.now = datetime(2026, 10, 20, 21, tzinfo=budget.TZ)

    def write_ledger(self, rows):
        with self.ledger.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=("email", "delivery_status", "sent_at", "run_date"))
            writer.writeheader()
            writer.writerows(rows)

    def reserve(self, address="new@example.test", gmail_count=0):
        return budget.reserve(self.db, address, "Company", "nightly-test", gmail_count,
                              now=self.now, ledger=self.ledger)

    def test_slot_450_allowed_and_451_blocked(self):
        stamp = self.now.isoformat()
        self.write_ledger([dict(email=f"old{i}@example.test", delivery_status="sent",
                                sent_at=stamp, run_date="2026-10-20") for i in range(449)])
        self.reserve(gmail_count=449)
        with patch.object(budget, "clock", return_value=self.now):
            budget.confirm(self.db, "new@example.test", "gmail-450", stamp)
        with self.assertRaisesRegex(ValueError, "limit"):
            self.reserve("one-too-many@example.test", 449)

    def test_midnight_does_not_reset_rolling_limit(self):
        stamp = self.now.replace(hour=0) - timedelta(minutes=5)
        self.write_ledger([dict(email=f"old{i}@example.test", delivery_status="sent",
                                sent_at=stamp.isoformat(), run_date="2026-10-19") for i in range(450)])
        self.assertEqual(budget.status(self.db, self.now, self.ledger)["sent_or_reserved_today"], 0)
        with self.assertRaisesRegex(ValueError, "limit"):
            self.reserve()

    def test_account_mail_outside_ledger_counts(self):
        with self.assertRaisesRegex(ValueError, "limit"):
            self.reserve(gmail_count=450)

    def test_pending_send_blocks_all_further_sends_even_next_day(self):
        self.reserve()
        self.assertEqual(budget.status(self.db, self.now + timedelta(days=2), self.ledger)["remaining"], 0)
        with self.assertRaisesRegex(ValueError, "pending"):
            self.reserve("other@example.test")

    def test_recipient_normalization_prevents_recontact(self):
        self.write_ledger([dict(email=" Known@Example.test ", delivery_status="sent_by_user",
                                sent_at="", run_date="2026-10-16")])
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.reserve("known@example.test")

    def test_confirmation_does_not_double_count_ledger(self):
        self.reserve()
        stamp = self.now.isoformat()
        with patch.object(budget, "clock", return_value=self.now):
            budget.confirm(self.db, "new@example.test", "gmail-message", stamp)
        self.write_ledger([dict(email="new@example.test", delivery_status="sent",
                                sent_at=stamp, run_date="2026-10-20")])
        result = budget.status(self.db, self.now, self.ledger)
        self.assertEqual(result["sent_or_reserved_24h"], 1)
        self.assertEqual(result["remaining"], 449)

    def test_naive_ledger_time_stops_sending(self):
        self.write_ledger([dict(email="old@example.test", delivery_status="sent",
                                sent_at="2026-10-20T20:00:00", run_date="2026-10-20")])
        with self.assertRaisesRegex(ValueError, "timezone"):
            self.reserve()

    def test_invalid_confirmation_keeps_reservation_pending(self):
        self.reserve()
        with self.assertRaises(ValueError):
            budget.confirm(self.db, "new@example.test", "", self.now.isoformat())
        self.assertTrue(budget.status(self.db, self.now, self.ledger)["pending"])


class RunnerTests(unittest.TestCase):
    def setUp(self):
        window = patch.object(nightly, "night_window", side_effect=lambda now: ("nightly-test", now + timedelta(hours=12)))
        self.real_window = nightly.night_window
        window.start()
        self.addCleanup(window.stop)

    def test_delayed_daytime_launch_is_skipped(self):
        now = datetime(2026, 10, 20, 14, tzinfo=budget.TZ)
        self.assertIsNone(self.real_window(now))
        self.assertIsNone(self.real_window(now.replace(hour=9)))
        campaign, end = self.real_window(now.replace(hour=21))
        self.assertEqual(campaign, "nightly-20261020")
        self.assertEqual(end, now.replace(day=21, hour=9))
        campaign, end = self.real_window(now.replace(day=21, hour=2))
        self.assertEqual(campaign, "nightly-20261020")
        self.assertEqual(end.hour, 9)

    def test_dry_run_does_not_launch_codex(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(nightly, "RUNS", Path(tmp)), \
                patch.object(nightly.subprocess, "Popen") as popen, redirect_stdout(io.StringIO()):
            self.assertEqual(nightly.run(dry_run=True), 0)
            popen.assert_not_called()

    def test_limit_or_pending_blocks_process_launch(self):
        for pending in ([], ["uncertain@example.test"]):
            with self.subTest(pending=pending), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                with patch.object(nightly, "ROOT", root), patch.object(nightly, "RUNS", root / "runs"), \
                        patch.object(nightly, "status", return_value={"pending": pending, "remaining": 0}), \
                        patch.object(nightly, "connect") as connect, \
                        patch.object(nightly.subprocess, "Popen") as popen, redirect_stdout(io.StringIO()):
                    (root / "runs").mkdir()
                    expected = 1 if pending else 0
                    self.assertEqual(nightly.run(), expected)
                    popen.assert_not_called()

    def test_no_progress_stops_instead_of_restarting_forever(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "runs").mkdir()
            (root / "NIGHTLY.md").write_text("One company")
            with patch.object(nightly, "ROOT", root), patch.object(nightly, "RUNS", root / "runs"), \
                    patch.object(nightly, "status", return_value={"pending": [], "remaining": 450}), \
                    patch.object(nightly, "connect") as connect, \
                    patch.object(nightly.subprocess, "Popen") as popen, redirect_stdout(io.StringIO()):
                connect.return_value.__enter__.return_value.execute.return_value.fetchone.return_value = (0,)
                popen.return_value.returncode = 0
                self.assertEqual(nightly.run(), 1)
                self.assertEqual(popen.call_count, 1)
                report = json.loads(next((root / "runs").glob("*/report.json")).read_text())
                self.assertEqual(report["status"], "no_verified_delivery")

    def test_schedule_has_no_immediate_or_continuous_run(self):
        job = schedule.definition()
        self.assertEqual(job["StartCalendarInterval"], {"Hour": 21, "Minute": 0})
        self.assertFalse(job["RunAtLoad"])
        self.assertNotIn("KeepAlive", job)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", nightly.command(Path("result")))


if __name__ == "__main__":
    unittest.main()
