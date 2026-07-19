import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "skills" / "agentic-commerce" / "seo-aeo-geo-audit" / "eval"
CASES = EVAL_DIR / "held-out-cases.json"
CONTRACT = EVAL_DIR / "check-contract.py"
HARNESS = EVAL_DIR / "run_harness.py"
TARGET_AGENT = EVAL_DIR / "run_target_agent.py"
VALIDATOR = EVAL_DIR / "validate-harness-results.py"
WORKFLOW = ROOT / ".github" / "workflows" / "seo-aeo-geo-audit-harness.yml"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def artifact_for(case: dict) -> dict:
    expected = case["expected"]
    artifact = {
        "disposition": expected["disposition"],
        "findings": [{"id": item} for item in expected["finding_ids"]],
        "recommendations": [{"id": item} for item in expected["recommendation_ids"]],
        "evidence": [{"source": item} for item in expected["evidence_sources"]],
    }
    if "route" in expected:
        artifact["route"] = expected["route"]
    return artifact


def records_for(cases: list[dict]) -> list[dict]:
    return [{
        "case_id": case["id"], "condition": condition, "trial": trial,
        "model": "test-model", "harness_version": "test-harness",
        "runner_protocol_version": "seo-aeo-geo-artifact-runner/v1",
        "skill_used": condition == "enabled" and case["expected_skill_usage"] == "use",
        "audit_artifact": artifact_for(case),
    } for case in cases for condition in ("enabled", "disabled") for trial in range(1, 6)]


class SeoAeoGeoAuditEvalTest(unittest.TestCase):
    def test_held_out_cases_are_balanced_with_structured_outcomes(self):
        cases = json.loads(CASES.read_text())["cases"]
        self.assertGreaterEqual(len(cases), 10)
        self.assertEqual(sum(case["expected_skill_usage"] == "use" for case in cases), 5)
        self.assertEqual(sum(case["expected_skill_usage"] == "do_not_use" for case in cases), 5)
        self.assertTrue(all(case["split"] == "held_out" for case in cases))
        self.assertTrue(all(case["expected"]["evidence_sources"] for case in cases))

    def test_contract_runner_is_offline_and_separate_from_outcome_scoring(self):
        result = subprocess.run(["python3", str(CONTRACT)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: deterministic SEO/AEO/GEO contract checks", result.stdout)
        self.assertNotIn("grade_artifact", CONTRACT.read_text())

    def test_validator_requires_artifact_evidence_not_pass_labels_or_phrases(self):
        validator = load_module(VALIDATOR, "seo_artifact_validator")
        cases = json.loads(CASES.read_text())["cases"]
        records = records_for(cases)
        for record in records:
            record["audit_artifact"] = {"outcome": "audit complete", "passed": True}
        failures, _ = validator.validate(records)
        self.assertTrue(any("/enabled is below" in failure for failure in failures))

    def test_validator_requires_enabled_delta_and_accepts_structured_evidence(self):
        validator = load_module(VALIDATOR, "seo_delta_validator")
        cases = json.loads(CASES.read_text())["cases"]
        records = records_for(cases)
        failures, _ = validator.validate(records)
        self.assertIn("aggregate enabled artifact outcome delta is below 2%", failures)
        next(record for record in records if record["condition"] == "disabled")["audit_artifact"] = {"disposition": "wrong"}
        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory) / "results.json"
            results.write_text(json.dumps(records))
            result = subprocess.run(["python3", str(VALIDATOR), "--results", str(results)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("aggregate artifact outcome delta", result.stdout)

    def test_validator_requires_correct_skill_use_for_each_condition(self):
        validator = load_module(VALIDATOR, "seo_skill_use_validator")
        cases = json.loads(CASES.read_text())["cases"]
        records = records_for(cases)
        next(record for record in records if record["case_id"] == "copy-rewrite" and record["condition"] == "enabled")["skill_used"] = True
        next(record for record in records if record["case_id"] == "canonical-and-sitemap" and record["condition"] == "disabled")["skill_used"] = True
        failures, _ = validator.validate(records)
        self.assertTrue(any("skill_used" in failure for failure in failures))

    def test_repository_target_agent_uses_only_workspace_inputs(self):
        target_agent = load_module(TARGET_AGENT, "seo_target_agent")
        validator = load_module(VALIDATOR, "seo_target_agent_validator")
        cases = json.loads(CASES.read_text())["cases"]
        audit_case = next(case for case in cases if case["id"] == "canonical-and-sitemap")
        route_case = next(case for case in cases if case["id"] == "copy-rewrite")
        self.assertNotIn("expected", TARGET_AGENT.read_text())
        self.assertTrue(target_agent.run(audit_case["prompt"], audit_case["input"], "enabled")["skill_used"])
        self.assertFalse(target_agent.run(audit_case["prompt"], audit_case["input"], "disabled")["skill_used"])
        self.assertFalse(target_agent.run(route_case["prompt"], route_case["input"], "enabled")["skill_used"])
        for case in cases:
            enabled = target_agent.run(case["prompt"], case["input"], "enabled")
            disabled = target_agent.run(case["prompt"], case["input"], "disabled")
            should_use = case["expected_skill_usage"] == "use"
            self.assertEqual(enabled["skill_used"], should_use)
            self.assertFalse(disabled["skill_used"])
            if should_use:
                self.assertTrue(validator.grade_artifact(case, enabled["audit_artifact"]))

    def test_isolated_harness_only_exposes_inputs_and_enabled_skill(self):
        harness = load_module(HARNESS, "seo_isolation_harness")
        case = json.loads(CASES.read_text())["cases"][0]
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            harness.prepare_workspace(workspace, case, "enabled")
            exposed = json.loads((workspace / "case.json").read_text())
            self.assertEqual(exposed, {"id": case["id"], "prompt": case["prompt"], "input": case["input"]})
            self.assertTrue((workspace / "SKILL.md").is_file())
            self.assertTrue((workspace / "checks.md").is_file())
            self.assertFalse(any("expected" in path.read_text() for path in workspace.iterdir() if path.is_file()))
        command = harness.isolated_command(Path("/tmp/seo-eval"), "image@sha256:abc", "declared-model", "enabled", 1)
        self.assertIn("--network", command)
        self.assertIn("none", command)
        self.assertIn("--read-only", command)
        self.assertIn("HOME=/nonexistent", HARNESS.read_text())

    def test_live_harness_is_manually_gated_and_retains_results(self):
        workflow = WORKFLOW.read_text()
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("if: inputs.run_harness", workflow)
        self.assertIn("timeout-minutes: 60", workflow)
        self.assertIn("concurrency:", workflow)
        self.assertIn("upload-artifact", workflow)
        self.assertIn("seo-aeo-geo-audit-results.json", workflow)
        self.assertIn("run_target_agent.py", workflow)
        self.assertNotIn("SEO_AEO_GEO_AUDIT_EVAL_RUNNER", workflow)
