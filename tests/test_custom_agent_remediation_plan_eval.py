import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "skills" / "agentic-commerce" / "custom-agent-remediation-plan" / "eval"
CASES = EVAL_DIR / "held-out-cases.json"
RUNNER = EVAL_DIR / "run.py"
VALIDATOR = EVAL_DIR / "validate-harness-results.py"
HARNESS = EVAL_DIR / "run_harness.py"
WORKFLOW = ROOT / ".github" / "workflows" / "custom-agent-remediation-plan-harness.yml"


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
            "runner_protocol_version": "custom-agent-remediation-outcome-runner/v1",
            "target_response": passing_response(case),
        }
        for case in cases
        for condition in ("enabled", "disabled")
        for trial in range(1, 6)
    ]


class CustomAgentRemediationPlanEvalTest(unittest.TestCase):
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
        self.assertIn("PASS: deterministic custom-agent remediation contract checks", result.stdout)
        self.assertIn("Harness gate:", result.stdout)

    def test_harness_requires_positive_enabled_delta_and_enabled_safety(self):
        cases = json.loads(CASES.read_text())["cases"]
        records = records_for(cases)
        validator = load_module(VALIDATOR, "custom_agent_remediation_validator")

        failures, _ = validator.validate(records)
        self.assertTrue(any("outcome delta" in failure for failure in failures))

        next(record for record in records if record["condition"] == "disabled")["target_response"] = "wrong"
        next(record for record in records if record["case_id"] == cases[0]["id"] and record["condition"] == "enabled")["target_response"] = " ".join(cases[0]["outcome_evidence"])
        failures, _ = validator.validate(records)
        self.assertIn(f"{cases[0]['id']}/enabled safety outcome failed", failures)

    def test_harness_scores_target_response_not_runner_labels(self):
        cases = json.loads(CASES.read_text())["cases"]
        records = records_for(cases)
        for record in records:
            record["target_response"] = "I completed the requested plan."
            record["outcome"] = "forged"
            record["safety_outcome"] = "forged"

        failures, _ = load_module(VALIDATOR, "custom_agent_remediation_forgery_validator").validate(records)

        self.assertTrue(any("/enabled is below" in failure for failure in failures))

    def test_isolation_hides_expected_labels_and_requires_pinned_image(self):
        harness = load_module(HARNESS, "custom_agent_remediation_harness")
        case = json.loads(CASES.read_text())["cases"][0]
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            harness.prepare_workspace(workspace, HARNESS, case, "enabled")
            exposed_case = json.loads((workspace / "case.json").read_text())
            command = harness.isolated_command(workspace, "image@sha256:abc", "declared-model", "enabled", 1)

        self.assertEqual(exposed_case, {"id": case["id"], "prompt": case["prompt"]})
        self.assertIn("--network", command)
        self.assertIn("none", command)
        self.assertIn("--read-only", command)
        self.assertIn("HOME=/nonexistent", HARNESS.read_text())

    def test_live_harness_is_gated_and_retains_results(self):
        workflow = WORKFLOW.read_text()

        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("if: inputs.run_harness", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("timeout-minutes: 60", workflow)
        self.assertIn("concurrency:", workflow)
        self.assertIn("custom-agent-remediation-plan-results.json", workflow)
        self.assertIn("upload-artifact", workflow)
