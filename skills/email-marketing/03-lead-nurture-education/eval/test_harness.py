#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path


EVAL = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("lead_nurture_harness", EVAL / "run_harness.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HarnessValidationTest(unittest.TestCase):
    def test_requires_an_enabled_improvement_over_disabled(self):
        keys = {"outcomes": {"case": {"decision": "HOLD", "required_actions": ["verify-consent"]}}}
        records = []
        for trial in range(3):
            records.append({"name": "case", "condition": "enabled", "trial": trial, "outcome": {"decision": "HOLD", "actions": ["verify-consent"]}})
            records.append({"name": "case", "condition": "disabled", "trial": trial, "outcome": {"decision": "SEND", "actions": []}})

        self.assertEqual(MODULE.validate(records, keys, 3), {"enabled_pass_rate": 1.0, "disabled_pass_rate": 0.0, "delta": 1.0})

    def test_rejects_duplicate_trial_records(self):
        keys = {"outcomes": {"case": {"decision": "HOLD", "required_actions": ["verify-consent"]}}}
        record = {"name": "case", "condition": "enabled", "trial": 0, "outcome": {"decision": "HOLD", "actions": ["verify-consent"]}}

        with self.assertRaises(ValueError):
            MODULE.validate([record, record], keys, 3)


if __name__ == "__main__":
    unittest.main()
