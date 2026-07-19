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

    def test_finds_a_latest_head_finding_after_the_first_page(self):
        comments = [
            {"id": index, "commit_id": "old", "user": {"login": "github-actions[bot]"}, "body": "<!-- ocr-page -->"}
            for index in range(100)
        ]
        comments.append({"id": 101, "commit_id": "latest", "user": {"login": "github-actions[bot]"}, "body": "<!-- ocr-page -->"})

        failures = governance.validate_ocr_dispositions(
            head_sha="latest",
            review_comments=comments,
            issue_comments=[],
            pr_commits=[{"sha": "latest"}],
        )

        self.assertEqual(failures, ["OCR finding 101 on latest head is undispositioned"])


class AgentLabelTests(unittest.TestCase):
    def test_rejects_bare_alias_and_preserves_historical_labels(self):
        fixture = json.loads((FIXTURES / "agent-labels.json").read_text())

        failures = governance.validate_agent_labels(**fixture)

        self.assertEqual(failures, ["Invalid agent label: agent:gpt5-high-reviewer"])

    def test_rejects_role_labels_when_model_id_is_unavailable(self):
        failures = governance.validate_pr_agent_metadata({
            "body": "\n".join([
                "- Resolved model ID: unavailable",
                "- Metadata limitation: runtime did not expose it",
                "- Verified agent labels: agent:gpt5-high-reviewer",
                "- Legacy agent labels: N/A",
            ]),
            "labels": [{"name": "agent:gpt5-high-reviewer"}],
        })

        self.assertEqual(failures, ["Invalid agent label: agent:gpt5-high-reviewer"])

    def test_requires_a_limitation_when_model_id_is_unavailable(self):
        failures = governance.validate_pr_agent_metadata({
            "body": "- Resolved model ID: unavailable\n- Metadata limitation: N/A",
            "labels": [],
        })

        self.assertEqual(failures, ["PR with unavailable model ID needs a metadata limitation"])

    def test_rejects_a_pr_label_that_does_not_match_the_recorded_model(self):
        failures = governance.validate_pr_agent_metadata({
            "body": "\n".join([
                "- Resolved model ID: gpt5.6-terra",
                "- Metadata limitation: N/A",
                "- Verified agent labels: agent:gpt5-high-reviewer",
                "- Legacy agent labels: N/A",
            ]),
            "labels": [{"name": "agent:gpt5-high-reviewer"}],
        })

        self.assertEqual(failures, ["Invalid agent label: agent:gpt5-high-reviewer"])

    def test_accepts_a_baselined_legacy_label_with_a_verified_current_label(self):
        failures = governance.validate_pr_agent_metadata({
            "body": "\n".join([
                "- Resolved model ID: gpt5.6-terra",
                "- Metadata limitation: N/A",
                "- Verified agent labels: agent:gpt5.6-terra-medium-fixer",
                "- Legacy agent labels: agent:gpt5-high-reviewer",
            ]),
            "labels": [
                {"name": "agent:gpt5.6-terra-medium-fixer"},
                {"name": "agent:gpt5-high-reviewer"},
            ],
        }, legacy_agent_labels={"agent:gpt5-high-reviewer"})

        self.assertEqual(failures, [])

    def test_rejects_a_new_label_declared_as_legacy(self):
        failures = governance.validate_pr_agent_metadata({
            "body": "\n".join([
                "- Resolved model ID: gpt5.6-terra",
                "- Metadata limitation: N/A",
                "- Verified agent labels: agent:gpt5.6-terra-medium-fixer",
                "- Legacy agent labels: agent:gpt5-high-reviewer",
            ]),
            "labels": [
                {"name": "agent:gpt5.6-terra-medium-fixer"},
                {"name": "agent:gpt5-high-reviewer"},
            ],
        }, legacy_agent_labels=set())

        self.assertIn("Invalid agent label: agent:gpt5-high-reviewer", failures)

    def test_rejects_an_unrecorded_agent_label(self):
        failures = governance.validate_pr_agent_metadata({
            "body": "\n".join([
                "- Resolved model ID: gpt5.6-terra",
                "- Metadata limitation: N/A",
                "- Verified agent labels: agent:gpt5.6-terra-medium-fixer",
                "- Legacy agent labels: N/A",
            ]),
            "labels": [
                {"name": "agent:gpt5.6-terra-medium-fixer"},
                {"name": "agent:gpt5-high-reviewer"},
            ],
        })

        self.assertEqual(failures, [
            "Invalid agent label: agent:gpt5-high-reviewer",
            "Unverified agent label: agent:gpt5-high-reviewer",
        ])


class RepositoryPolicyTests(unittest.TestCase):
    def test_requires_the_ocr_gate_for_the_default_branch(self):
        rulesets = [{
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
            "rules": [{
                "type": "required_status_checks",
                "parameters": {"required_status_checks": [{"context": "OCR disposition gate"}]},
            }],
        }]

        failures = governance.validate_required_status_check_policy(rulesets)

        self.assertEqual(failures, [])

    def test_rejects_a_policy_without_the_ocr_gate(self):
        failures = governance.validate_required_status_check_policy([])

        self.assertEqual(failures, ["Default branch must require OCR disposition gate"])


class OcrDispositionWorkflowTests(unittest.TestCase):
    def test_gate_is_rechecked_after_ocr_and_disposition_comments(self):
        workflow = GATE_WORKFLOW.read_text()

        self.assertIn("workflow_run:", workflow)
        self.assertIn("Open Code Review", workflow)
        self.assertIn("pull_request:", workflow)
        self.assertIn("issue_comment:", workflow)
        self.assertIn("statuses: write", workflow)
        self.assertIn("timeout-minutes: 10", workflow)
        self.assertIn("cancel-in-progress: true", workflow)
        self.assertIn("--pr-commits", workflow)
        self.assertIn("?ref=$HEAD_SHA", workflow)
        self.assertIn("/tmp/verify-pr-governance.py", workflow)
        self.assertIn("--paginate --slurp", workflow)
        self.assertIn("--pr /tmp/pr.json", workflow)
        self.assertIn("BASE_SHA", workflow)
        self.assertIn("legacy-agent-labels.json?ref=$BASE_SHA", workflow)
        self.assertIn("--legacy-agent-labels /tmp/legacy-agent-labels.json", workflow)


if __name__ == "__main__":
    unittest.main()
