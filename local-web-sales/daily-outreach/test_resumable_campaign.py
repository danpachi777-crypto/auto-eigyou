import unittest
from unittest.mock import Mock

from resumable_campaign import next_action, wait_online


class RecoveryTests(unittest.TestCase):
    def test_disconnect_waits_and_continues_only_after_connection_returns(self):
        record, sleep = Mock(), Mock()
        probe = Mock(side_effect=[False, False, True])
        self.assertTrue(wait_online(lambda: False, record, probe, sleep))
        self.assertEqual(sleep.call_count, 2)
        self.assertEqual(record.call_count, 2)

    def test_stop_while_offline_never_continues(self):
        sleep = Mock()
        self.assertFalse(wait_online(lambda: True, Mock(), lambda: False, sleep))
        sleep.assert_not_called()

    def test_pending_outcome_must_be_reconciled_even_at_limit_or_target(self):
        self.assertEqual(next_action({'pending': ['test@example.com'], 'remaining': 0},
                                     450, 450), 'reconcile')

    def test_limit_and_completion_end_this_run_without_scheduling_next_day(self):
        self.assertEqual(next_action({'pending': [], 'remaining': 0}, 2, 450), 'limit_reached')
        self.assertEqual(next_action({'pending': [], 'remaining': 100}, 450, 450), 'complete')
        self.assertEqual(next_action({'pending': [], 'remaining': 100}, 1, 450), 'send_one')


if __name__ == '__main__':
    unittest.main()
