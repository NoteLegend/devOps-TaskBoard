"""Verify that cloud eligibility failures stop the deployment guard."""
import datetime
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location('free_tier_guard', Path(__file__).with_name('check-free-tier.py'))
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class FreeTierGuardTest(unittest.TestCase):
    def state(self, **changes):
        state = {
            'accountId': '835582727900', 'accountPlanType': 'FREE', 'accountPlanStatus': 'ACTIVE',
            'accountPlanRemainingCredits': {'amount': 117.2, 'unit': 'USD'},
            'accountPlanExpirationDate': (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=5)).isoformat(),
        }
        state.update(changes)
        return state

    def run_guard(self, state):
        with patch('sys.argv', ['check-free-tier.py', '--account', '835582727900']), \
             patch.object(guard.shutil, 'which', return_value='/mock/aws'), \
             patch.object(guard.subprocess, 'run', return_value=Mock(stdout=json.dumps(state))), \
             patch('builtins.print'):
            guard.main()

    def test_active_free_account_with_sufficient_credits(self):
        self.run_guard(self.state())

    def test_paid_plan_is_rejected_even_with_credits(self):
        with self.assertRaisesRegex(RuntimeError, 'ACTIVE FREE'):
            self.run_guard(self.state(accountPlanType='PAID'))

    def test_wrong_account_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'Wrong AWS account'):
            self.run_guard(self.state(accountId='123456789012'))

    def test_insufficient_credits_are_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'Insufficient'):
            self.run_guard(self.state(accountPlanRemainingCredits={'amount': 3.0, 'unit': 'USD'}))

    def test_expiring_plan_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'expires too soon'):
            self.run_guard(self.state(accountPlanExpirationDate=datetime.datetime.now(datetime.timezone.utc).isoformat()))

    def test_inactive_plan_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'ACTIVE FREE'):
            self.run_guard(self.state(accountPlanStatus='EXPIRED'))


if __name__ == '__main__':
    unittest.main()
