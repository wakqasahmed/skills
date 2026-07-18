import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "skills" / "email-marketing" / "00-email-marketing-guardrails" / "eval"


class EmailGuardrailsEvalTest(unittest.TestCase):
    def test_held_out_scenarios_balance_safe_outcomes_and_rejections(self) -> None:
        cases = json.loads((EVAL_DIR / "fixtures" / "held-out-scenarios.json").read_text())["cases"]

        self.assertGreaterEqual(len(cases), 10)
        self.assertEqual({case["split"] for case in cases}, {"held-out"})
        self.assertGreaterEqual(sum(case["expected"]["decision"] == "SEND" for case in cases), 5)
        self.assertGreaterEqual(sum(case["expected"]["decision"] != "SEND" for case in cases), 5)
        self.assertTrue(all("required_actions" in case["expected"] for case in cases))

    def test_deterministic_components_run_without_network(self) -> None:
        result = subprocess.run(
            ["bash", str(EVAL_DIR / "run-eval.sh")],
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: 12 held-out outcome scenarios", result.stdout)
        self.assertIn("PASS: static contract", result.stdout)
