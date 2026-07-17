import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "scripts" / "validate-plugin.py"
RETIRED_REPOSITORIES = (
    "wakqasahmed/ai-visibility-skills",
    "wakqasahmed/agentic-commerce-skills",
    "wakqasahmed/ai-engineering-workflow-skills",
    "wakqasahmed/php-laravel-filament-skills",
    "wakqasahmed/email-marketing-skills",
)


class ValidatePluginTest(unittest.TestCase):
    def make_repository(self) -> Path:
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        root = Path(temporary_directory.name)

        (root / "scripts").mkdir()
        shutil.copy2(VALIDATOR, root / "scripts" / "validate-plugin.py")
        (root / ".claude-plugin").mkdir()
        (root / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"skills": ["skills/example/example-skill"]})
        )
        (root / "skills" / "example" / "example-skill").mkdir(parents=True)
        (root / "skills" / "example" / "example-skill" / "SKILL.md").write_text("# Example\n")
        (root / "README.md").write_text("npx skills@latest add wakqasahmed/skills\n")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        return root

    def validate(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "scripts/validate-plugin.py"],
            cwd=root,
            text=True,
            capture_output=True,
        )

    def test_accepts_a_clean_repository(self) -> None:
        result = self.validate(self.make_repository())

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_retired_repositories_outside_the_readme(self) -> None:
        root = self.make_repository()
        retired_reference = root / "skills" / "example" / "reference.md"
        retired_reference.write_text("\n".join(RETIRED_REPOSITORIES))
        subprocess.run(["git", "add", str(retired_reference.relative_to(root))], cwd=root, check=True)

        result = self.validate(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("former source repos", result.stderr)
        self.assertIn("skills/example/reference.md", result.stderr)
        for repository in RETIRED_REPOSITORIES:
            self.assertIn(repository, result.stderr)

    def test_rejects_nested_source_sync_automation(self) -> None:
        root = self.make_repository()
        stale_script = root / "scripts" / "legacy" / "sync-repositories.py"
        stale_script.parent.mkdir()
        stale_script.write_text("print('obsolete')\n")
        subprocess.run(["git", "add", str(stale_script.relative_to(root))], cwd=root, check=True)

        result = self.validate(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source-sync automation", result.stderr)
        self.assertIn("scripts/legacy/sync-repositories.py", result.stderr)
