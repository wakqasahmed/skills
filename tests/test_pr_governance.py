import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "support" / "ai-engineering-workflow" / "scripts" / "verify-pr-governance.py"
FIXTURES = ROOT / "support" / "ai-engineering-workflow" / "fixtures" / "pr-governance"
GATE_WORKFLOW = ROOT / ".github" / "workflows" / "ocr-disposition-gate.yml"

spec = importlib.util.spec_from_file_location("verify_pr_governance", SCRIPT)
governance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(governance)


def run_governance_gate(pr, review_comments=(), issue_comments=()):
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        paths = {
            "review_comments": directory / "review-comments.json",
            "issue_comments": directory / "issue-comments.json",
            "pr_commits": directory / "pr-commits.json",
            "pr": directory / "pr.json",
            "legacy_agent_labels": directory / "legacy-agent-labels.json",
        }
        inputs = {
            "review_comments": list(review_comments),
            "issue_comments": list(issue_comments),
            "pr_commits": [],
            "pr": pr,
            "legacy_agent_labels": [],
        }
        for name, path in paths.items():
            path.write_text(json.dumps(inputs[name]))

        return subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "--head-sha", "latest",
                "--review-comments", str(paths["review_comments"]),
                "--issue-comments", str(paths["issue_comments"]),
                "--pr-commits", str(paths["pr_commits"]),
                "--pr", str(paths["pr"]),
                "--legacy-agent-labels", str(paths["legacy_agent_labels"]),
            ],
            capture_output=True,
            text=True,
            check=False,
        )


class OcrDispositionTests(unittest.TestCase):
    def test_gate_rejects_unsafe_public_output(self):
        safe_pr = {
            "body": "\n".join([
                "- Resolved model ID: gpt5.6-terra",
                "- Metadata limitation: N/A",
                "- Verified agent labels: N/A",
                "- Legacy agent labels: N/A",
            ]),
            "labels": [],
        }

        for public_input in (
            {"pr": {**safe_pr, "body": f"{safe_pr['body']}\nCredential: /tmp/credentials.json"}},
            {"review_comments": [{"body": "Credential: /tmp/credentials.json"}]},
            {"issue_comments": [{"body": "Credential: /tmp/credentials.json"}]},
        ):
            result = run_governance_gate(
                public_input.get("pr", safe_pr),
                public_input.get("review_comments", []),
                public_input.get("issue_comments", []),
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("Public output contains a local credential-file path", result.stdout)

    def test_gate_accepts_safe_public_output(self):
        result = run_governance_gate(
            {
                "body": "\n".join([
                    "- Resolved model ID: gpt5.6-terra",
                    "- Metadata limitation: N/A",
                    "- Verified agent labels: N/A",
                    "- Legacy agent labels: N/A",
                    "Credential: [redacted]",
                ]),
                "labels": [],
            },
            [{"body": "Token location: [redacted]"}],
            [{"body": "Credential: [redacted]"}],
        )

        self.assertEqual(result.returncode, 0, result.stdout)

    def test_gate_ignores_automated_review_text(self):
        result = run_governance_gate(
            {
                "body": "\n".join([
                    "- Resolved model ID: gpt5.6-terra",
                    "- Metadata limitation: N/A",
                    "- Verified agent labels: N/A",
                    "- Legacy agent labels: N/A",
                ]),
                "labels": [],
            },
            [{
                "user": {"login": "github-actions[bot]"},
                "body": "Credential: /tmp/credentials.json",
            }],
        )

        self.assertEqual(result.returncode, 0, result.stdout)

    def test_public_output_rejects_local_credential_file_paths(self):
        fixture = json.loads((FIXTURES / "public-output.json").read_text())

        for output in fixture["safe"]:
            self.assertEqual(governance.validate_public_output(output), [])
        for output in fixture["unsafe"]:
            self.assertEqual(
                governance.validate_public_output(output),
                ["Public output contains a local credential-file path"],
            )

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

    def test_requires_a_one_sentence_disposition_reason(self):
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
                    "body": "<!-- ocr-disposition:42 -->\nDisposition: fixed\nReason: Fixed.",
                }
            ],
            "pr_commits": [{"sha": "latest"}],
        }

        failures = governance.validate_ocr_dispositions(**fixture)

        self.assertEqual(failures, [])

    def test_rejects_verbose_disposition_evidence(self):
        failures = governance.disposition_error(
            43,
            {"disposition": "fixed", "reason": "Fixed in abc123.", "test": "python3 -m unittest"},
            False,
            {"abc123"},
        )

        self.assertEqual(failures, "OCR finding 43 must use only disposition and reason")

    def test_rejects_repeated_disposition_fields_and_unrecognised_content(self):
        fixture = {
            "head_sha": "latest",
            "review_comments": [
                {
                    "id": 44,
                    "commit_id": "latest",
                    "user": {"login": "github-actions[bot]"},
                    "body": "<!-- ocr-run-1 -->\nFinding",
                },
                {
                    "id": 45,
                    "commit_id": "latest",
                    "user": {"login": "github-actions[bot]"},
                    "body": "<!-- ocr-run-1 -->\nFinding",
                },
            ],
            "issue_comments": [
                {
                    "author_association": "MEMBER",
                    "body": "\n".join([
                        "<!-- ocr-disposition:44 -->",
                        "Disposition: fixed",
                        "Disposition: fixed",
                        "Reason: Fixed.",
                    ]),
                },
                {
                    "author_association": "MEMBER",
                    "body": "\n".join([
                        "<!-- ocr-disposition:45 -->",
                        "Disposition: fixed",
                        "Reason: Fixed.",
                        "Test: python3 -m unittest",
                    ]),
                },
            ],
            "pr_commits": [{"sha": "latest"}],
        }

        failures = governance.validate_ocr_dispositions(**fixture)

        self.assertEqual(failures, [
            "OCR finding 44 must use only disposition and reason",
            "OCR finding 45 must use only disposition and reason",
        ])

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
