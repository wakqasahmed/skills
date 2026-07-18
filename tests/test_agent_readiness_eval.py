import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "skills" / "agentic-commerce" / "agent-readiness" / "eval"
CASES = EVAL_DIR / "fixtures" / "held-out.json"
VALIDATOR = EVAL_DIR / "validate-harness-results.py"


class AgentReadinessEvalTest(unittest.TestCase):
    def test_held_out_cases_balance_skill_usage_and_safety(self):
        cases = json.loads(CASES.read_text())["cases"]

        self.assertGreaterEqual(len(cases), 10)
        self.assertEqual(sum(case["expected_skill_usage"] == "use" for case in cases), 5)
        self.assertEqual(sum(case["expected_skill_usage"] == "do_not_use" for case in cases), 5)
        self.assertTrue(all(case["split"] == "held_out" for case in cases))
        self.assertTrue(all(case["expected_safety_outcome"] for case in cases))

    def test_harness_validator_requires_enabled_disabled_trials(self):
        records = []
        for case in json.loads(CASES.read_text())["cases"]:
            for condition in ("enabled", "disabled"):
                for trial in range(1, 6):
                    records.append({
                        "case_id": case["id"],
                        "condition": condition,
                        "trial": trial,
                        "model": "test-model",
                        "harness_version": "test-harness-1",
                        "skill_used": (
                            condition == "enabled"
                            and case["expected_skill_usage"] == "use"
                        ),
                        "outcome": case["expected_outcome"],
                        "safety_outcome": case["expected_safety_outcome"],
                    })

        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory) / "results.json"
            results.write_text(json.dumps(records))
            result = subprocess.run(
                ["python3", str(VALIDATOR), "--results", str(results)],
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("outcome delta", result.stdout)
