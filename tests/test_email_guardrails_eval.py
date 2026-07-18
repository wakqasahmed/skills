import json
import importlib.util
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "skills" / "email-marketing" / "00-email-marketing-guardrails" / "eval"
HARNESS = EVAL_DIR / "run_harness.py"


def load_harness():
    spec = importlib.util.spec_from_file_location("email_guardrails_harness", HARNESS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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

    def test_harness_rejects_duplicate_trials_and_uses_network_namespace(self) -> None:
        harness = load_harness()
        cases = json.loads((EVAL_DIR / "fixtures" / "held-out-scenarios.json").read_text())["cases"]
        records = []
        for case in cases:
            for condition in ("enabled", "disabled"):
                for trial in range(3):
                    records.append({
                        "name": case["name"],
                        "condition": condition,
                        "trial": trial,
                        "outcome": case["expected"],
                    })

        with self.assertRaises(ValueError):
            harness.validate(records + [records[0]], cases, 3)
        self.assertEqual(harness.isolated_command(Path("runner"))[:3], ["unshare", "--net", "--"])
