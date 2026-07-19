import importlib.util
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "skills" / "engineering" / "workflow-router" / "eval" / "run-eval.sh"
EVALUATOR = RUNNER.with_name("evaluate.py")


def load_evaluator():
    spec = importlib.util.spec_from_file_location("workflow_router_eval", EVALUATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WorkflowRouterEvalTest(unittest.TestCase):
    def test_requests_select_the_smallest_route(self) -> None:
        evaluator = load_evaluator()

        self.assertEqual(evaluator.route_for("Checkout returns 500"), "bug")
        self.assertEqual(evaluator.route_for("Add one export field"), "small-feature")
        self.assertEqual(
            evaluator.route_for("Design a marketplace with independent slices"),
            "idea-to-staging",
        )
        self.assertEqual(
            evaluator.route_for("Run this claimed non-trivial GitHub issue"),
            "claimed-github-issue",
        )
        self.assertEqual(
            evaluator.route_for("Fix this claimed trivial GitHub issue"),
            "small-feature",
        )
        self.assertEqual(evaluator.route_for("Release the reviewed build"), "release")
        self.assertEqual(evaluator.route_for("DNS approval is missing"), "human-held-blocker")

    def test_router_behavioral_fixtures_pass_without_network(self) -> None:
        result = subprocess.run(["bash", RUNNER], cwd=ROOT, text=True, capture_output=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: bug", result.stdout)
        self.assertIn("PASS: small-feature", result.stdout)
        self.assertIn("PASS: large-multi-issue-feature", result.stdout)
        self.assertIn("PASS: release", result.stdout)
        self.assertIn("PASS: human-only-blocker", result.stdout)
