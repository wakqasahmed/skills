#!/usr/bin/env python3
"""Small deterministic tests for launch outcome scoring and workspace isolation."""
import json
import tempfile
import unittest
from pathlib import Path

from evaluate_outcomes import load_cases, validate_records
from run_harness import isolated_command, prepare_workspace, runner_metadata, validate_image_reference


class EvaluationTests(unittest.TestCase):
    def test_outcome_validator_scores_complete_ablation_records(self) -> None:
        cases, failures = load_cases()
        self.assertEqual(failures, [])
        records = [
            {"name": case["name"], "condition": condition, "trial": 0, "outcome": case["expected"]}
            for case in cases
            for condition in ("enabled", "disabled")
        ]

        failures, summary = validate_records(records, cases, 1)

        self.assertEqual(failures, [])
        self.assertEqual(summary["enabled_pass_rate"], 1)
        self.assertEqual(summary["disabled_pass_rate"], 1)
        self.assertEqual(summary["delta"], 0)

    def test_workspace_exposes_only_prompts_and_enabled_skill(self) -> None:
        cases, failures = load_cases()
        self.assertEqual(failures, [])
        runner = Path(__file__)
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            prepare_workspace(workspace, runner, "enabled", cases)
            public_cases = json.loads((workspace / "cases.json").read_text())
            self.assertNotIn("expected", public_cases["cases"][0])
            self.assertTrue((workspace / "SKILL.md").is_file())

        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            prepare_workspace(workspace, runner, "disabled", cases)
            self.assertFalse((workspace / "SKILL.md").exists())

    def test_outcome_validator_scores_a_disabled_miss_as_a_positive_delta(self) -> None:
        cases, failures = load_cases()
        self.assertEqual(failures, [])
        records = [
            {"name": case["name"], "condition": condition, "trial": 0, "outcome": case["expected"]}
            for case in cases
            for condition in ("enabled", "disabled")
        ]
        incorrect_index = 5
        records[incorrect_index]["outcome"] = {"decision": "SEND", "reason_code": "ALL_APPLICABLE_GATES_PASSED", "required_actions": ["send"]}

        failures, summary = validate_records(records, cases, 1)

        self.assertEqual(failures, [])
        self.assertEqual(summary["enabled_pass_rate"], 1)
        self.assertEqual(summary["disabled_pass_rate"], 11 / 12)
        self.assertAlmostEqual(summary["delta"], 1 / 12)

    def test_harness_does_not_expose_the_ablation_condition(self) -> None:
        command = isolated_command(Path("/tmp/workspace"), "example-image", 0, "example-model", "v1")

        self.assertNotIn("HARNESS_CONDITION=enabled", command)
        self.assertNotIn("enabled", command)

    def test_harness_rejects_a_mutable_image_tag(self) -> None:
        with self.assertRaisesRegex(ValueError, "digest-pinned"):
            validate_image_reference("registry.example/launch-harness:latest")
        validate_image_reference("registry.example/launch-harness@sha256:" + "a" * 64)

    def test_runner_metadata_records_revision_and_content_hash(self) -> None:
        metadata = runner_metadata(Path(__file__))

        self.assertRegex(metadata["runner_revision"], r"^[0-9a-f]{40}$")
        self.assertRegex(metadata["runner_sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
