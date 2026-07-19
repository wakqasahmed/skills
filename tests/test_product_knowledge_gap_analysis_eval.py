import importlib.util
import copy
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "skills" / "agentic-commerce" / "product-knowledge-gap-analysis" / "eval"
CASES = EVAL_DIR / "held-out-cases.json"
RUNNER = EVAL_DIR / "run.py"
VALIDATOR = EVAL_DIR / "validate-harness-results.py"
HARNESS = EVAL_DIR / "run_harness.py"
TARGET_RUNNER = EVAL_DIR / "runner.py"
WORKFLOW = ROOT / ".github" / "workflows" / "product-knowledge-gap-analysis-harness.yml"


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
            "runner_protocol_version": "product-knowledge-outcome-runner/v2",
            "artifact": copy.deepcopy(case["expected_artifact"]),
        }
        for case in cases
        for condition in ("enabled", "disabled")
        for trial in range(1, 6)
    ]


class ProductKnowledgeGapAnalysisEvalTest(unittest.TestCase):
    def test_held_out_cases_are_balanced_and_have_observable_artifacts(self):
        cases = json.loads(CASES.read_text())["cases"]

        self.assertGreaterEqual(len(cases), 10)
        self.assertGreaterEqual(sum(case["expected_skill_usage"] == "use" for case in cases), 5)
        self.assertGreaterEqual(sum(case["expected_skill_usage"] == "do_not_use" for case in cases), 5)
        self.assertTrue(all(case["split"] == "held_out" and isinstance(case["catalog"], list) and case["feed"] for case in cases))
        for case in (case for case in cases if case["expected_skill_usage"] == "use"):
            gap = case["expected_artifact"]["observed_gaps"][0]
            self.assertEqual(set(gap), {"sku", "field", "source", "remediation"})
        for case in (case for case in cases if case["expected_skill_usage"] == "do_not_use"):
            artifact = case["expected_artifact"]
            self.assertEqual(artifact["observed_gaps"], [])
            self.assertTrue(artifact["route"] and artifact["non_use_reason"])

    def test_deterministic_contract_runner_is_offline(self):
        result = subprocess.run(["python3", str(RUNNER)], text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: deterministic product-knowledge contract checks", result.stdout)

    def test_harness_requires_enabled_artifact_delta(self):
        cases = json.loads(CASES.read_text())["cases"]
        records = records_for(cases)
        validator = load_module(VALIDATOR, "product_knowledge_harness_validator")

        failures, _ = validator.validate(records)
        self.assertTrue(any("artifact delta" in failure for failure in failures))

        next(record for record in records if record["condition"] == "disabled")["artifact"] = {"decision": "wrong"}
        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory) / "results.json"
            results.write_text(json.dumps(records))
            result = subprocess.run(["python3", str(VALIDATOR), "--results", str(results)], text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("aggregate artifact delta", result.stdout)

    def test_harness_rejects_wrong_gap_product_source_and_remediation(self):
        cases = json.loads(CASES.read_text())["cases"]
        records = records_for(cases)
        enabled = [record for record in records if record["case_id"] == "allergen-ingredient-gap" and record["condition"] == "enabled"]
        enabled[0]["artifact"]["observed_gaps"][0]["sku"] = "SN-102"
        enabled[1]["artifact"]["observed_gaps"][0]["source"] = "catalog_owner"
        enabled[2]["artifact"]["observed_gaps"][0]["remediation"] = "invent_allergens"

        failures, _ = load_module(VALIDATOR, "product_knowledge_artifact_validator").validate(records)

        self.assertTrue(any("allergen-ingredient-gap/enabled is below" in failure for failure in failures))

    def test_executor_workspace_includes_catalog_feed_but_not_expectations(self):
        harness = load_module(HARNESS, "product_knowledge_isolation_harness")
        case = json.loads(CASES.read_text())["cases"][0]
        command = harness.isolated_command(Path("/tmp/product-knowledge-eval"), "image@sha256:abc", "declared-model")

        self.assertIn("--network", command)
        self.assertIn("none", command)
        self.assertIn("--read-only", command)
        self.assertIn("HARNESS_MODEL=declared-model", command)
        self.assertNotIn("HARNESS_CONDITION=enabled", command)
        self.assertFalse(any(argument.startswith("HARNESS_TRIAL=") for argument in command))
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            harness.prepare_workspace(workspace, case, "enabled")
            executor_case = json.loads((workspace / "case.json").read_text())
            self.assertEqual(set(executor_case), {"id", "prompt", "catalog", "feed"})
            self.assertNotIn("expected_artifact", executor_case)
            self.assertTrue((workspace / "SKILL.md").exists())
            (workspace / "SKILL.md").unlink()
            harness.prepare_workspace(workspace, case, "disabled")
            self.assertFalse((workspace / "SKILL.md").exists())

    def test_checked_in_runner_contract_and_live_gate_are_executable(self):
        runner = TARGET_RUNNER.read_text()
        workflow = WORKFLOW.read_text()

        self.assertIn('TARGET = "/usr/local/bin/product-knowledge-target"', runner)
        self.assertIn("input=json.dumps(request)", runner)
        self.assertNotIn("PRODUCT_KNOWLEDGE_EVAL_RUNNER", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("if: inputs.run_harness", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("timeout-minutes: 60", workflow)
        self.assertIn("product-knowledge-gap-analysis-results.json", workflow)

    def test_checked_in_runner_passes_only_executor_input_to_target(self):
        runner = load_module(TARGET_RUNNER, "product_knowledge_target_runner")
        case = json.loads(CASES.read_text())["cases"][0]
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "case.json").write_text(json.dumps({key: case[key] for key in ("id", "prompt", "catalog", "feed")}))
            result = type("Result", (), {"stdout": json.dumps(case["expected_artifact"])})()
            with patch.dict("os.environ", {"HARNESS_WORKSPACE": str(workspace), "HARNESS_MODEL": "offline-test"}, clear=True), patch.object(runner.subprocess, "run", return_value=result) as invoke, patch("builtins.print") as output:
                self.assertEqual(runner.main(), 0)

        request = json.loads(invoke.call_args.kwargs["input"])
        self.assertEqual(set(request), {"id", "prompt", "catalog", "feed", "skill"})
        self.assertNotIn("expected_artifact", request)
        self.assertEqual(request["skill"], None)
        self.assertEqual(invoke.call_args.kwargs["timeout"], runner.TARGET_TIMEOUT_SECONDS)
        self.assertEqual(json.loads(output.call_args.args[0])["artifact"], case["expected_artifact"])
