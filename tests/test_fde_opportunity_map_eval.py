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


def passing_response(case: dict) -> str:
    return " ".join([*case["outcome_evidence"], *case["safety_evidence"]])


def records_for(cases: list[dict]) -> list[dict]:
    return [
        {
            "case_id": case["id"],
            "condition": condition,
            "trial": trial,
            "model": "test-model",
            "harness_version": "test-harness-1",
            "runner_protocol_version": "fde-outcome-runner/v1",
            "target_response": passing_response(case),
        }
        for case in cases
        for condition in ("enabled", "disabled")
        for trial in range(1, 6)
    ]


class FdeOpportunityMapEvalTest(unittest.TestCase):
    def test_held_out_cases_are_balanced_and_outcome_based(self):
        cases = json.loads(CASES.read_text())["cases"]

        self.assertGreaterEqual(len(cases), 10)
        self.assertGreaterEqual(sum(case["expected_skill_usage"] == "use" for case in cases), 5)
        self.assertGreaterEqual(sum(case["expected_skill_usage"] == "do_not_use" for case in cases), 5)
        self.assertTrue(all(case["split"] == "held_out" for case in cases))
        self.assertTrue(all(case["expected_outcome"] and case["expected_safety_outcome"] for case in cases))
        self.assertTrue(all(case["outcome_evidence"] and case["safety_evidence"] for case in cases))

    def test_deterministic_contract_runner_is_offline(self):
        result = subprocess.run(["python3", str(RUNNER)], text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: deterministic FDE contract checks", result.stdout)
        self.assertIn("Harness gate:", result.stdout)

    def test_harness_requires_enabled_delta_and_no_safety_regression(self):
        cases = json.loads(CASES.read_text())["cases"]
        records = records_for(cases)

        validator = load_module(VALIDATOR, "fde_harness_validator")
        failures, _ = validator.validate(records)
        self.assertTrue(any("outcome delta" in failure for failure in failures))

        next(record for record in records if record["condition"] == "disabled")["target_response"] = "wrong"
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

    def test_workspace_does_not_expose_expected_labels_to_runner(self):
        harness = load_module(HARNESS, "fde_workspace_harness")
        case = json.loads(CASES.read_text())["cases"][0]

        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            harness.prepare_workspace(workspace, HARNESS, case, "enabled")
            exposed_case = json.loads((workspace / "case.json").read_text())

        self.assertEqual(exposed_case, {"id": case["id"], "prompt": case["prompt"]})

    def test_harness_scores_outcomes_from_target_response(self):
        validator = load_module(VALIDATOR, "fde_outcome_scoring_validator")
        cases = json.loads(CASES.read_text())["cases"]
        records = records_for(cases)

        failures, _ = validator.validate(records)

        self.assertEqual(failures, ["aggregate enabled outcome delta is below 2%"])

    def test_harness_rejects_forged_labels_without_target_response_evidence(self):
        validator = load_module(VALIDATOR, "fde_forged_labels_validator")
        cases = json.loads(CASES.read_text())["cases"]
        records = records_for(cases)
        for record in records:
            record["target_response"] = "I completed the requested work."
            record["outcome"] = next(case for case in cases if case["id"] == record["case_id"])["expected_outcome"]
            record["safety_outcome"] = next(case for case in cases if case["id"] == record["case_id"])["expected_safety_outcome"]

        failures, _ = validator.validate(records)

        self.assertTrue(any("/enabled is below" in failure for failure in failures))

    def test_harness_rejects_any_enabled_safety_failure(self):
        validator = load_module(VALIDATOR, "fde_safety_validator")
        cases = json.loads(CASES.read_text())["cases"]
        records = records_for(cases)

        next(record for record in records if record["case_id"] == "erp-order-sync" and record["condition"] == "enabled")["target_response"] = " ".join(cases[0]["outcome_evidence"])
        next(record for record in records if record["case_id"] == "pim-feed-normalization" and record["condition"] == "disabled")["target_response"] = " ".join(cases[1]["outcome_evidence"])
        next(record for record in records if record["case_id"] == "checkout-approval-workflow" and record["condition"] == "disabled")["target_response"] = " ".join(cases[2]["outcome_evidence"])
        next(record for record in records if record["condition"] == "disabled")["target_response"] = "wrong"

        failures, _ = validator.validate(records)

        self.assertIn("erp-order-sync/enabled safety outcome failed", failures)

    def test_live_harness_is_manually_gated_and_retains_results(self):
        workflow = WORKFLOW.read_text()

        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("if: inputs.run_harness", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("timeout-minutes: 60", workflow)
        self.assertIn("concurrency:", workflow)
        self.assertIn("fde-opportunity-map-results.json", workflow)
        self.assertIn("upload-artifact", workflow)
