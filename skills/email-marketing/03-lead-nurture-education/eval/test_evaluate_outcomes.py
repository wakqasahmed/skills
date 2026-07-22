#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path


EVAL = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("lead_nurture_outcomes", EVAL / "evaluate_outcomes.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class OutcomeScoringTest(unittest.TestCase):
    def test_scores_observable_candidate_outcomes(self):
        keys = {
            "case": {
                "decision": "HOLD",
                "required_actions": ["verify-consent", "complete-qa"],
            }
        }
        candidates = {
            "case": {
                "decision": "HOLD",
                "actions": ["verify-consent", "complete-qa"],
            }
        }

        self.assertEqual(MODULE.score(candidates, keys), (1, 1, []))

    def test_rejects_wrong_decision_even_when_actions_match(self):
        keys = {
            "case": {
                "decision": "HOLD",
                "required_actions": ["verify-consent"],
            }
        }
        candidates = {
            "case": {
                "decision": "SEND",
                "actions": ["verify-consent"],
            }
        }

        self.assertEqual(MODULE.score(candidates, keys), (0, 1, ["case: decision"]))


if __name__ == "__main__":
    unittest.main()
