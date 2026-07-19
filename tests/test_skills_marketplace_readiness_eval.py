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
TARGET_RUNNER = EVAL_DIR / "target_agent_runner.py"
WORKFLOW = ROOT / ".github" / "workflows" / "skills-marketplace-readiness-harness.yml"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def records_for(cases: list[dict], disabled_valid: bool = True) -> list[dict]:
    validator = load_module(VALIDATOR, "marketplace_expected")
    expected = validator.expected_outcomes()
    records = []
    for case in cases:
        for condition in ("enabled", "disabled"):
            artifact = {"schema_version": 1, "safety": "no_external_action", **expected[case["id"]]}
            if condition == "disabled" and not disabled_valid:
                artifact["action"] = "wrong_action"
            for trial in range(1, 6):
                records.append({
                    "case_id": case["id"], "condition": condition, "trial": trial,
                    "model": "test-model", "harness_version": "test-harness-2",
                    "runner_protocol_version": "marketplace-readiness-agent-runner/v2",
                    "outcome_artifact": artifact,
                })
    return records


class SkillsMarketplaceReadinessEvalTest(unittest.TestCase):
    def test_held_out_cases_have_realistic_repositories_and_balanced_no_use_outcomes(self):
        cases = json.loads(CASES.read_text())["cases"]
        expected = load_module(VALIDATOR, "marketplace_case_expected").expected_outcomes()

        self.assertGreaterEqual(len(cases), 10)
        self.assertGreaterEqual(sum(expected[case["id"]]["verdict"] == "out_of_scope" for case in cases), 5)
        self.assertTrue(all(case["split"] == "held_out" for case in cases))
        self.assertTrue(all((EVAL_DIR / "fixtures" / "repos" / case["fixture"]).is_dir() for case in cases))

    def test_deterministic_contract_runner_is_offline(self):
        result = subprocess.run(["python3", str(RUNNER)], text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: deterministic marketplace readiness contract checks", result.stdout)

    def test_harness_requires_enabled_delta(self):
        cases = json.loads(CASES.read_text())["cases"]
        validator = load_module(VALIDATOR, "marketplace_validator")
        failures, _ = validator.validate(records_for(cases))
        self.assertTrue(any("artifact delta" in failure for failure in failures))

        failures, reports = validator.validate(records_for(cases, disabled_valid=False))
        self.assertFalse(failures, failures)
        self.assertIn("aggregate artifact delta +100%", reports)

    def test_harness_exposes_only_fixture_prompt_and_optional_skill(self):
        harness = load_module(HARNESS, "marketplace_harness")
        case = json.loads(CASES.read_text())["cases"][0]
        command = harness.isolated_command(Path("/tmp/marketplace-eval"), "image@sha256:abc", "declared-model", "enabled", 1)
        self.assertIn("--network", command)
        self.assertIn("none", command)
        self.assertIn("--read-only", command)
        self.assertIn("/workspace/target_agent_runner.py", command)
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            harness.prepare_workspace(workspace, case, "disabled")
            self.assertFalse((workspace / "SKILL.md").exists())
            self.assertFalse((workspace / "expected-outcomes.json").exists())
            self.assertEqual(json.loads((workspace / "request.json").read_text()), {"prompt": case["prompt"], "artifact_path": "/tmp/outcome.json"})
            self.assertTrue((workspace / "repository").is_dir())

    def test_validator_rejects_forged_action_and_missing_fixture_evidence(self):
        cases = json.loads(CASES.read_text())["cases"]
        records = records_for(cases, disabled_valid=False)
        for record in records:
            if record["case_id"] == cases[0]["id"] and record["condition"] == "enabled":
                record["outcome_artifact"] = {"schema_version": 1, "safety": "no_external_action", "verdict": "ready", "action": "publish", "evidence": ["invented.txt"]}

        failures, _ = load_module(VALIDATOR, "marketplace_forgery_validator").validate(records)
        self.assertTrue(any("/enabled is below" in failure for failure in failures))

    def test_validator_rejects_enabled_safety_regression(self):
        cases = json.loads(CASES.read_text())["cases"]
        records = records_for(cases, disabled_valid=False)
        for record in records:
            if record["condition"] == "enabled":
                record["outcome_artifact"]["safety"] = "external_action"

        failures, _ = load_module(VALIDATOR, "marketplace_safety_validator").validate(records)
        self.assertTrue(any("safety outcome failed" in failure for failure in failures))
        self.assertIn("aggregate enabled safety regression", failures)

    def test_checked_in_runner_invokes_declared_target_agent(self):
        runner = TARGET_RUNNER.read_text()
        self.assertIn("/opt/marketplace-agent/bin/agent", runner)
        self.assertIn('"--model"', runner)
        self.assertIn('"--repository"', runner)
        self.assertIn('"--output"', runner)
        self.assertIn('"--skill"', runner)

    def test_live_harness_is_manually_gated_and_retains_results(self):
        workflow = WORKFLOW.read_text()
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("if: inputs.run_harness", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("timeout-minutes: 60", workflow)
        self.assertIn("SKILLS_MARKETPLACE_READINESS_EVAL_IMAGE", workflow)
        self.assertNotIn("EVAL_RUNNER", workflow)
        self.assertIn("skills-marketplace-readiness-results.json", workflow)
        self.assertIn("upload-artifact", workflow)
