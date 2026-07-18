import importlib.util
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "eval" / "run-trigger-evals.py"
CASES = ROOT / "eval" / "trigger-cases.json"


def load_runner():
    spec = importlib.util.spec_from_file_location("trigger_evals", RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TriggerEvalTest(unittest.TestCase):
    def test_every_skill_has_a_realistic_positive_and_near_miss(self):
        data = json.loads(CASES.read_text())
        discovered = {str(path.parent.relative_to(ROOT / "skills")) for path in (ROOT / "skills").glob("*/*/SKILL.md")}
        self.assertEqual({case["skill"] for case in data["cases"]}, discovered)
        self.assertEqual(len(data["cases"]), len(discovered))
        self.assertEqual({case["category"] for case in data["cases"]}, set(data["minimum_metrics"]))
        for case in data["cases"]:
            self.assertTrue(case["positive"])
            self.assertTrue(case["negative"])
            self.assertFalse(load_runner().matches(case["negative"], case["terms"]), case["skill"])

    def test_runner_passes_train_and_validation_without_network(self):
        for split in ("train", "validation"):
            result = subprocess.run(["python3", str(RUNNER), "--split", split], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("precision=1.00 recall=1.00", result.stdout)
