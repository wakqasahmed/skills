import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY_ROOT / "scripts" / "validate-plugin.py"
REPOSITORY_OWNER = "wakqasahmed/"
RETIRED_REPOSITORIES = tuple(
    REPOSITORY_OWNER + name
    for name in (
        "ai-visibility-skills",
        "agentic-commerce-skills",
        "ai-engineering-workflow-skills",
        "php-laravel-filament-skills",
        "email-marketing-skills",
    )
)


class ValidatePluginTest(unittest.TestCase):
    def test_open_code_review_workflow_contract(self) -> None:
        workflow = (
            REPOSITORY_ROOT / ".github" / "workflows" / "open-code-review.yml"
        ).read_text()

        self.assertIn("pull_request:\n    types: [opened, synchronize, reopened]", workflow)
        self.assertNotIn("pull_request_target:", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("pull-requests: write", workflow)
        self.assertIn("uses: alibaba/open-code-review@v1.7.12", workflow)
        self.assertIn(
            "if: github.event.pull_request.head.repo.full_name == github.repository",
            workflow,
        )
        ocr_inputs = re.findall(
            r"^          (llm_(?:url|auth_token|model|use_anthropic)): (.+)$",
            workflow,
            flags=re.MULTILINE,
        )
        self.assertEqual(
            ocr_inputs,
            [
                ("llm_url", "${{ secrets.OCR_LLM_URL }}"),
                ("llm_auth_token", "${{ secrets.OCR_LLM_AUTH_TOKEN }}"),
                ("llm_model", "${{ secrets.OCR_LLM_MODEL }}"),
                ("llm_use_anthropic", "${{ secrets.OCR_USE_ANTHROPIC }}"),
            ],
        )
        self.assertIn("sticky_summary: 'true'", workflow)
        self.assertIn("incremental: 'true'", workflow)

    def write_readme(self, root: Path, skill_paths: list[str]) -> None:
        categories: dict[str, list[str]] = {}
        for skill_path in skill_paths:
            _, category, skill = skill_path.split("/")
            categories.setdefault(category, []).append(skill)

        navigation = []
        for category, skills in sorted(categories.items()):
            navigation.append(f"### [{category.title()}](skills/{category}/)")
            navigation.extend(
                f"- [{skill}](skills/{category}/{skill}/)" for skill in skills
            )

        (root / "README.md").write_text(
            "npx skills@latest add wakqasahmed/skills\n\n## Browse Skills\n\n"
             + "\n".join(navigation)
             + "\n"
        )

    def make_repository(self) -> Path:
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        root = Path(temporary_directory.name)

        (root / "scripts").mkdir()
        shutil.copy2(VALIDATOR, root / "scripts" / "validate-plugin.py")
        (root / ".claude-plugin").mkdir()
        skill_paths = [
            "skills/example/example-skill",
            "skills/other/other-skill",
        ]
        (root / ".claude-plugin" / "plugin.json").write_text(json.dumps({"skills": skill_paths}))
        (root / "skills" / "example" / "example-skill").mkdir(parents=True)
        (root / "skills" / "example" / "example-skill" / "SKILL.md").write_text("# Example\n")
        (root / "skills" / "other" / "other-skill").mkdir(parents=True)
        (root / "skills" / "other" / "other-skill" / "SKILL.md").write_text("# Other\n")
        self.write_readme(root, skill_paths)
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

    def test_rejects_source_sync_workflows(self) -> None:
        root = self.make_repository()
        workflow = root / ".github" / "workflows" / "sync-check.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text("name: Legacy sync\n")
        subprocess.run(["git", "add", str(workflow.relative_to(root))], cwd=root, check=True)

        result = self.validate(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source-sync automation", result.stderr)
        self.assertIn(".github/workflows/sync-check.yml", result.stderr)

    def test_rejects_missing_or_duplicate_skill_navigation(self) -> None:
        root = self.make_repository()
        readme = root / "README.md"
        readme.write_text(
            readme.read_text().replace(
                "- [other-skill](skills/other/other-skill/)\n", ""
            ).replace(
                "- [example-skill](skills/example/example-skill/)\n",
                "- [example-skill](skills/example/example-skill/)\n"
                "- [example-skill](skills/example/example-skill/)\n",
            )
        )
        subprocess.run(["git", "add", "README.md"], cwd=root, check=True)

        result = self.validate(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("README skill navigation", result.stderr)
