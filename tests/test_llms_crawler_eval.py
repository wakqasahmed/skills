import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "skills" / "agentic-commerce" / "llms-txt-and-crawler-access" / "eval"
CASES = EVAL_DIR / "held-out-cases.json"
CONTRACT = EVAL_DIR / "check-contract.py"
VALIDATOR = EVAL_DIR / "validate-harness-results.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("llms_crawler_harness", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LlmsCrawlerEvalTest(unittest.TestCase):
    def test_held_out_cases_are_balanced_and_crawler_specific(self):
        cases = json.loads(CASES.read_text())["cases"]

        self.assertGreaterEqual(len(cases), 10)
        self.assertEqual(sum(case["expected_skill_usage"] == "use" for case in cases), 5)
        self.assertEqual(sum(case["expected_skill_usage"] == "do_not_use" for case in cases), 5)
        self.assertTrue(all(case["split"] == "held_out" for case in cases))
        self.assertTrue(all(case["expected_safety_outcome"] for case in cases))

    def test_static_contract_runs_in_a_disposable_offline_workspace(self):
        result = subprocess.run(
            ["bash", str(EVAL_DIR / "run-eval.sh")],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: llms/crawler static contract", result.stdout)

    def test_static_contract_rejects_invalid_skill_usage(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            eval_dir = workspace / "eval"
            eval_dir.mkdir()
            (workspace / "SKILL.md").write_text((EVAL_DIR.parent / "SKILL.md").read_text())
            cases = json.loads(CASES.read_text())
            cases["cases"][0]["expected_skill_usage"] = "invalid"
            (eval_dir / "held-out-cases.json").write_text(json.dumps(cases))
            (eval_dir / "check-contract.py").write_text(CONTRACT.read_text())
            result = subprocess.run(
                ["python3", str(eval_dir / "check-contract.py")],
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid expected_skill_usage 'invalid'", result.stdout)

    def test_harness_validator_reports_invalid_results_file(self):
        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory) / "results.json"
            results.write_text("{")
            result = subprocess.run(
                ["python3", str(VALIDATOR), "--results", str(results)],
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR: invalid results JSON", result.stdout)

    def test_harness_validator_reports_missing_results_file(self):
        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory) / "missing.json"
            result = subprocess.run(
                ["python3", str(VALIDATOR), "--results", str(results)],
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR: cannot read results", result.stdout)

    def test_harness_validator_names_invalid_record_fields(self):
        validator = load_validator()
        failures, _ = validator.validate([{
            "case_id": "missing",
            "condition": "unknown",
            "trial": 0,
        }])

        self.assertIn("invalid case_id: missing", failures)

    def test_harness_validator_requires_ablation_delta(self):
        cases = json.loads(CASES.read_text())["cases"]
        records = []
        for case in cases:
            for condition in ("enabled", "disabled"):
                for trial in range(1, 6):
                    records.append({
                        "case_id": case["id"],
                        "condition": condition,
                        "trial": trial,
                        "model": "test-model",
                        "harness_version": "test-harness-1",
                        "skill_used": condition == "enabled" and case["expected_skill_usage"] == "use",
                        "outcome": case["expected_outcome"],
                        "safety_outcome": case["expected_safety_outcome"],
                    })

        validator = load_validator()
        failures, _ = validator.validate(records)
        self.assertTrue(any("outcome delta" in failure for failure in failures))

        next(record for record in records if record["condition"] == "disabled")["outcome"] = "wrong"
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
        self.assertIn("aggregate outcome delta", result.stdout)
