import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "support" / "ai-engineering-workflow" / "scripts" / "verify-pr-governance.py"
FIXTURES = ROOT / "support" / "ai-engineering-workflow" / "fixtures" / "pr-governance"
GATE_WORKFLOW = ROOT / ".github" / "workflows" / "ocr-disposition-gate.yml"

spec = importlib.util.spec_from_file_location("verify_pr_governance", SCRIPT)
governance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(governance)


class OcrDispositionTests(unittest.TestCase):
    def test_late_latest_head_finding_blocks_until_dispositioned(self):
        fixture = json.loads((FIXTURES / "late-ocr-comments.json").read_text())

        failures = governance.validate_ocr_dispositions(**fixture)

        self.assertEqual(failures, ["OCR finding 22 on latest head is undispositioned"])

    def test_fixed_deferred_and_declined_dispositions_are_accepted(self):
        fixture = json.loads((FIXTURES / "disposition-outcomes.json").read_text())

        failures = governance.validate_ocr_dispositions(**fixture)

        self.assertEqual(failures, [])

    def test_blocking_finding_requires_a_fixed_disposition(self):
        fixture = json.loads((FIXTURES / "blocking-finding.json").read_text())

        failures = governance.validate_ocr_dispositions(**fixture)

        self.assertEqual(failures, ["Blocking OCR finding 31 must be fixed"])

    def test_rejects_an_unauthorized_disposition(self):
        fixture = {
            "head_sha": "latest",
            "review_comments": [
                {
                    "id": 41,
                    "commit_id": "latest",
                    "user": {"login": "github-actions[bot]"},
                    "body": "<!-- ocr-run-1 -->\nFinding",
                }
            ],
            "issue_comments": [
                {
                    "user": {"login": "external-user"},
                    "author_association": "CONTRIBUTOR",
                    "body": "<!-- ocr-disposition:41 -->\nDisposition: declined\nReason: Not applicable.",
                }
            ],
            "pr_commits": [{"sha": "latest"}],
        }

        failures = governance.validate_ocr_dispositions(**fixture)

        self.assertEqual(failures, ["OCR finding 41 has no authorized disposition"])

    def test_rejects_fixed_evidence_from_outside_the_pr(self):
        fixture = {
            "head_sha": "latest",
            "review_comments": [
                {
                    "id": 42,
                    "commit_id": "latest",
                    "user": {"login": "github-actions[bot]"},
                    "body": "<!-- ocr-run-1 -->\nFinding",
                }
            ],
            "issue_comments": [
                {
                    "user": {"login": "maintainer"},
                    "author_association": "MEMBER",
                    "body": "<!-- ocr-disposition:42 -->\nDisposition: fixed\nCommit: unrelated\nTest: python3 -m unittest tests.test_pr_governance",
                }
            ],
            "pr_commits": [{"sha": "latest"}],
        }

        failures = governance.validate_ocr_dispositions(**fixture)

        self.assertEqual(failures, ["Fixed OCR finding 42 needs a commit on this PR"])


class AgentLabelTests(unittest.TestCase):
    def test_rejects_bare_alias_and_preserves_historical_labels(self):
        fixture = json.loads((FIXTURES / "agent-labels.json").read_text())

        failures = governance.validate_agent_labels(**fixture)

        self.assertEqual(failures, ["Invalid agent label: agent:gpt5-high-reviewer"])


class OcrDispositionWorkflowTests(unittest.TestCase):
    def test_gate_is_rechecked_after_ocr_and_disposition_comments(self):
        workflow = GATE_WORKFLOW.read_text()

        self.assertIn("workflow_run:", workflow)
        self.assertIn("Open Code Review", workflow)
        self.assertIn("issue_comment:", workflow)
        self.assertIn("statuses: write", workflow)
        self.assertIn("--pr-commits", workflow)


if __name__ == "__main__":
    unittest.main()
