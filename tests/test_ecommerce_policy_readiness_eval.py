import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "skills" / "agentic-commerce" / "ecommerce-policy-readiness" / "eval"
CASES = EVAL_DIR / "held-out-cases.json"
VALIDATOR = EVAL_DIR / "validate-harness-results.py"
HARNESS = EVAL_DIR / "run_harness.py"
RUNNER = EVAL_DIR / "run.py"
WORKFLOW = ROOT / ".github" / "workflows" / "ecommerce-policy-readiness-harness.yml"


def load_validator():
    spec = importlib.util.spec_from_file_location("policy_readiness_harness", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_harness():
    spec = importlib.util.spec_from_file_location("policy_readiness_harness_runner", HARNESS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_contract_runner():
    spec = importlib.util.spec_from_file_location("policy_readiness_contract_runner", RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EcommercePolicyReadinessEvalTest(unittest.TestCase):
    def test_held_out_cases_are_balanced_and_outcome_based(self):
        cases = json.loads(CASES.read_text())["cases"]

        self.assertEqual(len(cases), 10)
        self.assertEqual(sum(case["expected_skill_usage"] == "use" for case in cases), 5)
        self.assertEqual(sum(case["expected_skill_usage"] == "do_not_use" for case in cases), 5)
        self.assertTrue(all(case["split"] == "held_out" for case in cases))
        self.assertTrue(all(case["expected_outcome"] and case["expected_safety_outcome"] for case in cases))

    def test_deterministic_contract_runner_is_offline(self):
        result = subprocess.run(["python3", str(EVAL_DIR / "run.py")], text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: static contract and held-out schema", result.stdout)

    def test_contract_rule_mutations_are_rejected(self):
        runner = load_contract_runner()
        rule = runner.RULES[0]

        self.assertIn(rule, runner.missing_rules(""))
        self.assertIn(rule, runner.missing_rules(rule.replace("never infer", "infer")))

    def complete_records(self):
        cases = json.loads(CASES.read_text())["cases"]
        records = []
        for case in cases:
            for condition in ("enabled", "disabled"):
                for trial in range(1, 6):
                    records.append({
                        "case_id": case["id"], "condition": condition, "trial": trial,
                        "model": "test-model", "harness_version": "test-harness-1",
                        "skill_used": condition == "enabled" and case["expected_skill_usage"] == "use",
                        "outcome": case["expected_outcome"],
                        "safety_outcome": case["expected_safety_outcome"],
                    })

        return records

    def test_harness_requires_positive_enabled_delta(self):
        records = self.complete_records()
        validator = load_validator()
        failures, _ = validator.validate(records)
        self.assertTrue(any("outcome delta" in failure for failure in failures))

        next(record for record in records if record["condition"] == "disabled")["outcome"] = "wrong"
        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory) / "results.json"
            results.write_text(json.dumps(records))
            result = subprocess.run(["python3", str(VALIDATOR), "--results", str(results)], text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("aggregate outcome delta", result.stdout)

    def test_harness_rejects_enabled_safety_regression(self):
        records = self.complete_records()
        next(record for record in records if record["condition"] == "enabled")["safety_outcome"] = "unsafe"

        failures, _ = load_validator().validate(records)

        self.assertTrue(any("safety regression" in failure for failure in failures))

    def test_checked_in_harness_uses_network_isolated_disposable_workspaces(self):
        harness = load_harness()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            runner = workspace.parent / "approved-runner"
            runner.write_text("#!/bin/sh\n")
            runner.chmod(0o755)
            self.addCleanup(runner.unlink)
            harness.prepare_workspace(workspace, runner, {"id": "case"}, "enabled")
            command = harness.isolated_command(workspace, "approved-harness@sha256:deadbeef", "enabled", 1)
            self.assertTrue((workspace / "case.json").exists())

        self.assertIn("--network", command)
        self.assertIn("none", command)
        self.assertIn("--read-only", command)
        self.assertIn("HARNESS_CONDITION=enabled", command)
        self.assertIn("HARNESS_TRIAL=1", command)
        self.assertFalse(any(str(ROOT) in argument for argument in command))

    def test_live_harness_is_manually_gated_with_read_only_permissions(self):
        workflow = WORKFLOW.read_text()

        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("if: inputs.run_harness", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("run_harness.py", workflow)
        self.assertIn("timeout-minutes: 60", workflow)
        self.assertIn("concurrency:", workflow)
        self.assertIn("ecommerce-policy-readiness-results.json", workflow)
