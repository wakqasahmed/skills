import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "skills" / "agentic-commerce" / "fde-opportunity-map" / "eval"
CASES = EVAL_DIR / "held-out-cases.json"
RUNNER = EVAL_DIR / "run.py"
VALIDATOR = EVAL_DIR / "validate-harness-results.py"
HARNESS = EVAL_DIR / "run_harness.py"
WORKFLOW = ROOT / ".github" / "workflows" / "fde-opportunity-map-harness.yml"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FdeOpportunityMapEvalTest(unittest.TestCase):
    def test_held_out_cases_are_balanced_and_outcome_based(self):
        cases = json.loads(CASES.read_text())["cases"]

        self.assertGreaterEqual(len(cases), 10)
        self.assertGreaterEqual(sum(case["expected_skill_usage"] == "use" for case in cases), 5)
        self.assertGreaterEqual(sum(case["expected_skill_usage"] == "do_not_use" for case in cases), 5)
        self.assertTrue(all(case["split"] == "held_out" for case in cases))
        self.assertTrue(all(case["expected_outcome"] and case["expected_safety_outcome"] for case in cases))

    def test_deterministic_contract_runner_is_offline(self):
        result = subprocess.run(["python3", str(RUNNER)], text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: deterministic FDE contract checks", result.stdout)
        self.assertIn("Harness gate:", result.stdout)

    def test_harness_requires_enabled_delta_and_no_safety_regression(self):
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

        validator = load_module(VALIDATOR, "fde_harness_validator")
        failures, _ = validator.validate(records)
        self.assertTrue(any("outcome delta" in failure for failure in failures))

        next(record for record in records if record["condition"] == "disabled")["outcome"] = "wrong"
        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory) / "results.json"
            results.write_text(json.dumps(records))
            result = subprocess.run(["python3", str(VALIDATOR), "--results", str(results)], text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("aggregate outcome delta", result.stdout)
        self.assertIn("aggregate safety delta", result.stdout)

    def test_harness_rejects_malformed_result_records(self):
        validator = load_module(VALIDATOR, "fde_malformed_harness_validator")

        failures, _ = validator.validate(["not a record"])

        self.assertIn("record must be an object", failures)

    def test_isolation_runner_requires_pinned_image_and_repository_runner(self):
        harness = load_module(HARNESS, "fde_isolation_harness")

        command = harness.isolated_command(Path("/tmp/fde-eval"), "image@sha256:abc", "declared-model", "enabled", 1)
        self.assertIn("--network", command)
        self.assertIn("none", command)
        self.assertIn("--read-only", command)
        self.assertIn("HARNESS_MODEL=declared-model", command)
        self.assertIn("HOME=/nonexistent", HARNESS.read_text())

    def test_live_harness_is_manually_gated_and_retains_results(self):
        workflow = WORKFLOW.read_text()

        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("if: inputs.run_harness", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("fde-opportunity-map-results.json", workflow)
        self.assertIn("upload-artifact", workflow)
