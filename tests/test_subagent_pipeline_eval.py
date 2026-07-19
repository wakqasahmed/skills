import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "skills" / "engineering" / "subagent-pipeline" / "eval"
HARNESS = EVAL_DIR / "run_harness.py"


def load_harness():
    spec = importlib.util.spec_from_file_location("subagent_pipeline_harness", HARNESS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SubagentPipelineEvalTest(unittest.TestCase):
    def test_runner_workspace_excludes_expected_answer_keys(self):
        harness = load_harness()
        case = json.loads((EVAL_DIR / "fixtures" / "held-out.json").read_text())["cases"][0]

        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            runner = workspace.parent / "approved-runner"
            runner.write_text("#!/bin/sh\n")
            runner.chmod(0o755)
            self.addCleanup(runner.unlink)

            harness.prepare_workspace(workspace, runner, case, "enabled")

            runner_case = json.loads((workspace / "case.json").read_text())

        self.assertEqual(
            runner_case,
            {"prompt": case["prompt"]},
        )
        self.assertNotIn("expected_outcome", runner_case)
        self.assertNotIn("expected_safety_outcome", runner_case)

    def test_runner_must_attest_declared_model(self):
        harness = load_harness()

        command = harness.isolated_command(
            Path("/workspace"), "runner@sha256:abc", "enabled", 1, "test-model"
        )

        self.assertIn("HARNESS_MODEL=test-model", command)
        harness.require_declared_model({"model": "test-model"}, "test-model")
        with self.assertRaisesRegex(SystemExit, "declared model"):
            harness.require_declared_model({"model": "other-model"}, "test-model")
