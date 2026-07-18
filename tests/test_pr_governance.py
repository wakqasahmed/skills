import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "support" / "ai-engineering-workflow" / "scripts" / "verify-pr-governance.py"
FIXTURES = ROOT / "support" / "ai-engineering-workflow" / "fixtures" / "pr-governance"

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


class AgentLabelTests(unittest.TestCase):
    def test_rejects_bare_alias_and_preserves_historical_labels(self):
        fixture = json.loads((FIXTURES / "agent-labels.json").read_text())

        failures = governance.validate_agent_labels(**fixture)

        self.assertEqual(failures, ["Invalid agent label: agent:gpt5-high-reviewer"])


if __name__ == "__main__":
    unittest.main()
