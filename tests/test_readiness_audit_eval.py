import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "skills" / "agentic-commerce" / "readiness-audit" / "eval"
CASES = EVAL_DIR / "held-out-cases.json"
RUNNER = EVAL_DIR / "run.py"
HARNESS = EVAL_DIR / "run_harness.py"
VALIDATOR = EVAL_DIR / "validate-harness-results.py"
WORKFLOW = ROOT / ".github" / "workflows" / "readiness-audit-outcome-eval.yml"


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
            "runner_protocol_version": "readiness-audit-runner/v2",
            "execution": {"exit_code": 0, "provided_inputs": {"protocol_version": "readiness-audit-runner/v2", "files": ["case.json", "fixture.html", *(["SKILL.md"] if condition == "enabled" else [])], "sha256": {name: "0" * 64 for name in ["case.json", "fixture.html", *(["SKILL.md"] if condition == "enabled" else [])]}}, "loaded_files": ["case.json", "fixture.html", *(["SKILL.md"] if condition == "enabled" else [])]},
            "target_response": passing_response(case),
        }
        for case in cases
        for condition in ("enabled", "disabled")
        for trial in range(1, 6)
    ]


class ReadinessAuditEvalTest(unittest.TestCase):
    def test_held_out_cases_are_balanced_and_fixture_grounded(self):
        cases = json.loads(CASES.read_text())["cases"]

        self.assertGreaterEqual(len(cases), 10)
        self.assertGreaterEqual(sum(case["expected_skill_usage"] == "use" for case in cases), 5)
        self.assertGreaterEqual(sum(case["expected_skill_usage"] == "do_not_use" for case in cases), 5)
        self.assertTrue(all(case["split"] == "held_out" for case in cases))
        self.assertTrue(all(case["fixture"] and case["fixture_evidence"] and case["outcome_evidence"] and case["safety_evidence"] for case in cases))

    def test_deterministic_contract_is_offline_and_rejects_rule_mutations(self):
        result = subprocess.run(["python3", str(RUNNER)], text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: deterministic readiness-audit contract checks", result.stdout)
        runner = load_module(RUNNER, "readiness_audit_contract")
        self.assertIn(runner.RULES[0], runner.missing_rules(""))

    def test_validator_requires_execution_outcome_and_safety_delta(self):
        cases = json.loads(CASES.read_text())["cases"]
        validator = load_module(VALIDATOR, "readiness_audit_validator")
        records = records_for(cases)

        failures, _ = validator.validate(records)
        self.assertTrue(any("outcome delta" in failure for failure in failures))

        for record in [record for record in records if record["condition"] == "disabled"][:2]:
            record["target_response"] = "wrong"
        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory) / "results.json"
            results.write_text(json.dumps(records))
            result = subprocess.run(["python3", str(VALIDATOR), "--results", str(results)], text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("aggregate outcome delta", result.stdout)
        self.assertIn("aggregate safety delta", result.stdout)

    def test_isolated_harness_passes_only_prompt_fixture_check_and_enabled_skill(self):
        harness = load_module(HARNESS, "readiness_audit_harness")
        case = json.loads(CASES.read_text())["cases"][0]
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            harness.prepare_workspace(workspace, HARNESS, case, "enabled")
            exposed_case = json.loads((workspace / "case.json").read_text())
            input_check = json.loads((workspace / "input-check.json").read_text())
            command = harness.isolated_command(workspace, "image@sha256:abc", "declared-model", "enabled", 1)
            self.assertTrue((workspace / "SKILL.md").is_file())

        self.assertEqual(exposed_case, {"id": case["id"], "prompt": case["prompt"]})
        self.assertEqual(input_check["files"], ["case.json", "fixture.html", "SKILL.md"])
        self.assertNotIn("expected_outcome", json.dumps(exposed_case))
        self.assertIn("--network", command)
        self.assertIn("none", command)
        self.assertIn("--read-only", command)
        self.assertIn("HARNESS_CONDITION=enabled", command)
        self.assertIn("--case", command)
        self.assertIn("/workspace/input-check.json", command)
        self.assertIn("--skill", command)
        self.assertIn("HOME=/nonexistent", HARNESS.read_text())

    def test_gated_workflow_retains_results(self):
        workflow = WORKFLOW.read_text()

        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("if: inputs.run_harness", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("timeout-minutes: 60", workflow)
        self.assertIn("concurrency:", workflow)
        self.assertIn("readiness-audit-results.json", workflow)
        self.assertIn("upload-artifact", workflow)
