#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

from evaluate_outcomes import score_records


FIXTURES = Path(__file__).parent / "fixtures"


class OutcomeScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.prompts = json.loads((FIXTURES / "held-out-prompts.json").read_text())["cases"]
        self.key = json.loads((FIXTURES / "outcome-key.json").read_text())["outcomes"]
        self.candidates = json.loads((FIXTURES / "candidate-outcomes.json").read_text())["records"]

    def test_scores_the_frozen_candidate_outcomes(self) -> None:
        summary = score_records(self.candidates, self.prompts, self.key)

        self.assertEqual(summary, {"passed": 10, "total": 10, "pass_rate": 1.0})

    def test_rejects_a_near_miss_that_keeps_inviting_a_registrant(self) -> None:
        records = [*self.candidates]
        records[5] = {**records[5], "outcome": {**records[5]["outcome"], "invite_exit": "after-event"}}

        summary = score_records(records, self.prompts, self.key)

        self.assertEqual(summary["passed"], 9)


if __name__ == "__main__":
    unittest.main()
