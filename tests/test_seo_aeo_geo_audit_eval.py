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

    def test_isolated_harness_only_exposes_inputs_and_enabled_skill(self):
        harness = load_module(HARNESS, "seo_isolation_harness")
        case = json.loads(CASES.read_text())["cases"][0]
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            harness.prepare_workspace(workspace, HARNESS, case, "enabled")
            exposed = json.loads((workspace / "case.json").read_text())
            self.assertEqual(exposed, {"id": case["id"], "prompt": case["prompt"], "input": case["input"]})
            self.assertTrue((workspace / "SKILL.md").is_file())
            self.assertTrue((workspace / "checks.md").is_file())
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
