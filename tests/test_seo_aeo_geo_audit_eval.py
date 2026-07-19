import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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
        "model": "test-model", "model_version": "test-model-2026-07", "harness_version": "test-harness",
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

    def test_repository_target_agent_forwards_model_and_enabled_skill_to_external_agent(self):
        target_agent = load_module(TARGET_AGENT, "seo_target_agent")
        cases = json.loads(CASES.read_text())["cases"]
        audit_case = next(case for case in cases if case["id"] == "canonical-and-sitemap")
        self.assertNotIn("expected", TARGET_AGENT.read_text())
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            harness = load_module(HARNESS, "seo_target_agent_harness")
            target_workspace = harness.prepare_workspace(workspace, audit_case, "enabled")
            request = target_agent.workspace_request(target_workspace, "declared-model")
        self.assertEqual(request["model"], "declared-model")
        self.assertEqual(request["prompt"], audit_case["prompt"])
        self.assertIn("cite the observed output", request["skill"])
        self.assertIn("Indexability and canonical URL", request["checks"])
        self.assertNotIn("expected", json.dumps(request))
        self.assertNotIn("condition", request)
        self.assertNotIn(audit_case["id"], json.dumps(request))

    def test_target_agent_response_requires_model_version_attestation(self):
        target_agent = load_module(TARGET_AGENT, "seo_target_agent_attestation")
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "input.json").write_text(json.dumps({"prompt": "Audit this.", "input": {"observations": []}}))
            (workspace / "SKILL.md").write_text("required skill guidance")
            (workspace / "checks.md").write_text("required audit checks")
            response = {"model": "declared-model", "model_version": "declared-model-2026-07", "skill_used": True, "audit_artifact": {"disposition": "audit"}}
            agent = workspace / "agent"
            agent.write_text("#!/usr/bin/env python3\nimport json, sys\nrequest = json.load(sys.stdin)\nassert request['model'] == 'declared-model'\nassert request['skill'] == 'required skill guidance'\nassert request['checks'] == 'required audit checks'\nprint(json.dumps(" + repr(response) + "))\n")
            agent.chmod(0o755)
            previous = os.environ.copy()
            try:
                os.environ.update({"HARNESS_WORKSPACE": str(workspace), "HARNESS_MODEL": "declared-model", "TARGET_AGENT_COMMAND": str(agent)})
                result = subprocess.run(["python3", str(TARGET_AGENT)], text=True, capture_output=True)
            finally:
                os.environ.clear()
                os.environ.update(previous)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        record = json.loads(result.stdout)
        self.assertEqual(record["model_version"], "declared-model-2026-07")

    def test_openrouter_runner_requires_an_environment_key_and_uses_the_fixed_api(self):
        target_agent = load_module(TARGET_AGENT, "seo_openrouter_runner")
        request = {"model": "nvidia/nemotron-3-super-120b-a12b:free", "prompt": "Audit this.", "input": {"observations": []}}
        previous = os.environ.copy()
        try:
            os.environ.pop("OPENROUTER_API_KEY", None)
            with self.assertRaises(SystemExit) as error:
                target_agent.run_openrouter_agent(request)
        finally:
            os.environ.clear()
            os.environ.update(previous)
        self.assertEqual(str(error.exception), "OPENROUTER_API_KEY is required for the openrouter runner")
        self.assertEqual(target_agent.OPENROUTER_API_URL, "https://openrouter.ai/api/v1/chat/completions")
        self.assertIn('environment["OPENROUTER_API_KEY"] = os.environ.get("OPENROUTER_API_KEY", "")', HARNESS.read_text())

    def test_openrouter_runner_returns_the_provider_artifact_without_following_redirects(self):
        target_agent = load_module(TARGET_AGENT, "seo_openrouter_response")
        request = {"model": "declared-model", "prompt": "Audit this.", "input": {"observations": []}}
        provider_response = {"choices": [{"message": {"content": json.dumps({"skill_used": False, "audit_artifact": {"disposition": "route"}})}}]}

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return json.dumps(provider_response).encode()

        class Opener:
            def open(self, http_request, timeout):
                self.request = http_request
                self.timeout = timeout
                return Response()

        opener = Opener()
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key", "HARNESS_MODEL_VERSION": "approved-version"}, clear=False), patch.object(target_agent.urllib.request, "build_opener", return_value=opener):
            response = target_agent.run_openrouter_agent(request)
        self.assertEqual(opener.request.full_url, target_agent.OPENROUTER_API_URL)
        self.assertEqual(opener.timeout, 120)
        self.assertEqual(response, {"model": "declared-model", "model_version": "approved-version", "skill_used": False, "audit_artifact": {"disposition": "route"}})

    def test_openrouter_runner_retries_rate_limits_using_retry_after(self):
        target_agent = load_module(TARGET_AGENT, "seo_openrouter_rate_limit")
        request = {"model": "declared-model", "prompt": "Audit this.", "input": {"observations": []}}
        provider_response = {"choices": [{"message": {"content": json.dumps({"skill_used": True, "audit_artifact": {"disposition": "audit"}})}}]}

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return json.dumps(provider_response).encode()

        class Opener:
            def __init__(self):
                self.calls = 0

            def open(self, http_request, timeout):
                self.calls += 1
                if self.calls == 1:
                    raise target_agent.urllib.error.HTTPError(http_request.full_url, 429, "rate limited", {"Retry-After": "3"}, None)
                return Response()

        opener = Opener()
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key", "HARNESS_MODEL_VERSION": "approved-version"}, clear=False), patch.object(target_agent.urllib.request, "build_opener", return_value=opener), patch.object(target_agent.time, "sleep") as sleep:
            response = target_agent.run_openrouter_agent(request)
        self.assertEqual(opener.calls, 2)
        sleep.assert_called_once_with(3)
        self.assertTrue(response["skill_used"])

    def test_openrouter_runner_honors_the_provider_rate_limit_reset(self):
        target_agent = load_module(TARGET_AGENT, "seo_openrouter_reset")
        with patch.object(target_agent.time, "time", return_value=1_784_449_740):
            delay = target_agent.rate_limit_delay({"X-RateLimit-Reset": "1784449800000"}, 0)
        self.assertEqual(delay, 60)

    def test_isolated_harness_keeps_case_labels_and_condition_outside_target_workspace(self):
        harness = load_module(HARNESS, "seo_isolation_harness")
        case = json.loads(CASES.read_text())["cases"][0]
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            for condition in ("enabled", "disabled"):
                target_workspace = harness.prepare_workspace(workspace / condition, case, condition)
                exposed = json.loads((target_workspace / "input.json").read_text())
                contents = "\n".join(path.read_text() for path in target_workspace.iterdir() if path.is_file())
                self.assertEqual(exposed, {"prompt": case["prompt"], "input": case["input"]})
                self.assertEqual((target_workspace / "SKILL.md").is_file(), condition == "enabled")
                self.assertEqual((target_workspace / "checks.md").is_file(), condition == "enabled")
                self.assertNotIn(case["id"], contents)
                self.assertNotIn(condition, contents)
                self.assertFalse((target_workspace / "case.json").exists())
        command = harness.isolated_command(Path("/tmp/seo-eval"), "image@sha256:abc", "declared-model")
        self.assertIn("--network", command)
        self.assertIn("none", command)
        self.assertIn("--read-only", command)
        self.assertIn("HOME=/nonexistent", HARNESS.read_text())
        self.assertNotIn("HARNESS_CONDITION", command)
        self.assertNotIn("HARNESS_TRIAL", command)

    def test_live_harness_is_manually_gated_and_retains_results(self):
        workflow = WORKFLOW.read_text()
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("if: inputs.run_harness", workflow)
        self.assertIn("timeout-minutes: 60", workflow)
        self.assertIn("concurrency:", workflow)
        self.assertIn("upload-artifact", workflow)
        self.assertIn("seo-aeo-geo-audit-results.json", workflow)
        self.assertIn("run_target_agent.py", workflow)
        self.assertIn("SEO_AEO_GEO_AUDIT_EVAL_MODEL", workflow)
        self.assertNotIn("SEO_AEO_GEO_AUDIT_EVAL_RUNNER", workflow)

    def test_openrouter_live_eval_is_explicitly_selected_and_documented(self):
        workflow = WORKFLOW.read_text()
        readme = (EVAL_DIR / "README.md").read_text()
        self.assertIn("runner:", workflow)
        self.assertIn("openrouter", workflow)
        self.assertIn("secrets.OPENROUTER_API_KEY", workflow)
        self.assertIn("inputs.runner == 'openrouter' && github.ref == 'refs/heads/main'", workflow)
        self.assertIn("OPENROUTER_API_KEY", readme)
        self.assertIn("nvidia/nemotron-3-super-120b-a12b:free", readme)
        self.assertIn("never pull-request CI", readme)

    def test_default_runner_does_not_receive_the_openrouter_secret(self):
        workflow = WORKFLOW.read_text()
        isolated_step = workflow.split("      - name: Run OpenRouter evaluator")[0]
        self.assertIn("default: isolated", isolated_step)
        self.assertIn("shell: bash", isolated_step)
        self.assertNotIn("OPENROUTER_API_KEY", isolated_step)
