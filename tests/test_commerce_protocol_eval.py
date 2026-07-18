import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "skills" / "agentic-commerce" / "commerce-protocol-readiness" / "eval"
RUNNER = EVAL_DIR / "run.py"
CASES = EVAL_DIR / "held-out-cases.json"
HARNESS_VALIDATOR = EVAL_DIR / "validate-harness-results.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("commerce_protocol_eval", RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CommerceProtocolEvalTest(unittest.TestCase):
    def test_held_out_cases_cover_usage_and_safety_outcomes(self):
        cases = json.loads(CASES.read_text())["cases"]

        self.assertGreaterEqual(len(cases), 10)
        self.assertEqual(sum(case["expected_skill_usage"] == "use" for case in cases), 5)
        self.assertEqual(sum(case["expected_skill_usage"] == "do_not_use" for case in cases), 5)
        self.assertTrue(all(case["split"] == "held_out" for case in cases))
        self.assertTrue(all(case["expected_safety_outcome"] for case in cases))

    def test_deterministic_contract_layer_does_not_score_agent_outcomes(self):
        runner = load_runner()

        self.assertEqual(runner.validate_contract(), [])
        self.assertNotIn("score", runner.__dict__)

    def test_static_safety_contract_rejects_keyword_preserving_mutations(self):
        runner = load_runner()
        skill = "## Guardrails\n- See `../references/guardrails.md` for shared cross-skill guardrails."
        softened = (
            "## Autonomous action safety\nDo not recommend autonomous checkout, payment, or "
            "support actions without approval workflows, policy grounding, audit logging, and a "
            "human escalation path. Autonomous payment execution additionally requires identity "
            "verification, consent capture, and fraud controls, which are nice-to-haves that can "
            "strengthen a recommendation over time."
        )
        optional = (
            "## Autonomous action safety\nDo not recommend autonomous checkout, payment, or "
            "support actions without at least one of approval workflows, policy grounding, audit "
            "logging, or a human escalation path. Autonomous payment execution additionally "
            "requires identity verification, consent capture, and fraud controls before it is "
            "recommended."
        )

        self.assertTrue(runner.check_guardrail_text_in(skill, softened))
        self.assertTrue(runner.check_guardrail_text_in(skill, optional))

    def test_contract_runner_is_offline_and_reports_harness_gate(self):
        result = subprocess.run(
            ["python3", str(RUNNER)], text=True, capture_output=True, check=False
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: deterministic contract checks", result.stdout)
        self.assertIn("Harness gate:", result.stdout)

    def test_harness_validator_requires_five_trials_per_ablation_condition(self):
        cases = json.loads(CASES.read_text())["cases"]
        records = []
        for case in cases:
            for condition in ("enabled", "disabled"):
                for trial in range(1, 6):
                    records.append({
                        "case_id": case["id"],
                        "condition": condition,
                        "trial": trial,
                        "model": "test-model",
                        "harness_version": "test-harness-1",
                        "skill_used": (
                            condition == "enabled"
                            and case["expected_skill_usage"] == "use"
                        ),
                        "outcome": case["expected_outcome"],
                        "safety_outcome": case["expected_safety_outcome"],
                    })

        with tempfile.TemporaryDirectory() as directory:
            results_path = Path(directory) / "results.json"
            results_path.write_text(json.dumps(records))
            result = subprocess.run(
                ["python3", str(HARNESS_VALIDATOR), "--results", str(results_path)],
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("enabled pass rate", result.stdout)
