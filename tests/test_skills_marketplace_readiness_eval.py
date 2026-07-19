import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "skills" / "agentic-commerce" / "skills-marketplace-readiness" / "eval"
CASES = EVAL_DIR / "held-out-cases.json"
RUNNER = EVAL_DIR / "run.py"
VALIDATOR = EVAL_DIR / "validate-harness-results.py"
HARNESS = EVAL_DIR / "run_harness.py"
WORKFLOW = ROOT / ".github" / "workflows" / "skills-marketplace-readiness-harness.yml"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def records_for(cases: list[dict]) -> list[dict]:
    return [
        {
            "case_id": case["id"], "condition": condition, "trial": trial,
            "model": "test-model", "harness_version": "test-harness-1",
            "runner_protocol_version": "marketplace-readiness-outcome-runner/v1",
            "target_response": " ".join([*case["outcome_evidence"], *case["safety_evidence"]]),
        }
        for case in cases
        for condition in ("enabled", "disabled")
        for trial in range(1, 6)
    ]


class SkillsMarketplaceReadinessEvalTest(unittest.TestCase):
    def test_held_out_cases_are_balanced_and_outcome_based(self):
        cases = json.loads(CASES.read_text())["cases"]

        self.assertGreaterEqual(len(cases), 10)
        self.assertGreaterEqual(sum(case["expected_skill_usage"] == "use" for case in cases), 5)
        self.assertGreaterEqual(sum(case["expected_skill_usage"] == "do_not_use" for case in cases), 5)
        self.assertTrue(all(case["split"] == "held_out" for case in cases))
        self.assertTrue(all(case["outcome_evidence"] and case["safety_evidence"] for case in cases))

    def test_deterministic_contract_runner_is_offline(self):
        result = subprocess.run(["python3", str(RUNNER)], text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: deterministic marketplace readiness contract checks", result.stdout)
        self.assertIn("Harness gate:", result.stdout)

    def test_harness_requires_enabled_delta_and_no_safety_regression(self):
        cases = json.loads(CASES.read_text())["cases"]
        records = records_for(cases)
        validator = load_module(VALIDATOR, "marketplace_validator")

        failures, _ = validator.validate(records)
        self.assertTrue(any("outcome delta" in failure for failure in failures))

        next(record for record in records if record["condition"] == "disabled")["target_response"] = "wrong"
        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory) / "results.json"
            results.write_text(json.dumps(records))
            result = subprocess.run(["python3", str(VALIDATOR), "--results", str(results)], text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("aggregate outcome delta", result.stdout)

    def test_harness_isolates_target_agent_and_hides_expected_labels(self):
        harness = load_module(HARNESS, "marketplace_harness")
        case = json.loads(CASES.read_text())["cases"][0]

        command = harness.isolated_command(Path("/tmp/marketplace-eval"), "image@sha256:abc", "declared-model", "enabled", 1)
        self.assertIn("--network", command)
        self.assertIn("none", command)
        self.assertIn("--read-only", command)
        self.assertIn("HARNESS_MODEL=declared-model", command)
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            harness.prepare_workspace(workspace, HARNESS, case, "enabled")
            exposed_case = json.loads((workspace / "case.json").read_text())
        self.assertEqual(exposed_case, {"id": case["id"], "prompt": case["prompt"]})

    def test_harness_rejects_forged_labels_without_response_evidence(self):
        cases = json.loads(CASES.read_text())["cases"]
        records = records_for(cases)
        for record in records:
            record["target_response"] = "The requested work is complete."
            record["outcome"] = "forged"
            record["safety_outcome"] = "forged"

        failures, _ = load_module(VALIDATOR, "marketplace_forgery_validator").validate(records)

        self.assertTrue(any("/enabled is below" in failure for failure in failures))

    def test_live_harness_is_manually_gated_and_retains_results(self):
        workflow = WORKFLOW.read_text()

        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("if: inputs.run_harness", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("timeout-minutes: 60", workflow)
        self.assertIn("concurrency:", workflow)
        self.assertIn("skills-marketplace-readiness-results.json", workflow)
        self.assertIn("upload-artifact", workflow)
