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
TAXONOMY = {
    "Agentic Commerce": {"agentic-commerce"},
    "AI Visibility": {"ai-visibility"},
    "Email Marketing": {"email-marketing"},
    "Engineering Workflow": {"engineering"},
    "PHP/Laravel/Filament": {"php", "laravel", "filament"},
    "Productivity/Product": {"productivity", "product"},
}
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
    def test_readme_documents_category_discovery_fallback(self) -> None:
        readme = (REPOSITORY_ROOT / "README.md").read_text()

        self.assertIn(
            "skills.sh does not support repository-defined marketplace groups.",
            readme,
        )

    def test_readme_uses_the_required_category_taxonomy(self) -> None:
        readme = (REPOSITORY_ROOT / "README.md").read_text()

        self.assertEqual(
            re.findall(r"^### (.+)$", readme, flags=re.MULTILINE),
            [
                "Agentic Commerce",
                "AI Visibility",
                "Email Marketing",
                "Engineering Workflow",
                "PHP/Laravel/Filament",
                "Productivity/Product",
            ],
        )

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
                ("llm_url", "${{ vars.OCR_LLM_URL }}"),
                ("llm_auth_token", "${{ secrets.OCR_LLM_AUTH_TOKEN }}"),
                ("llm_model", "${{ vars.OCR_LLM_MODEL }}"),
                ("llm_use_anthropic", "${{ vars.OCR_USE_ANTHROPIC }}"),
            ],
        )
        self.assertIn("sticky_summary: 'true'", workflow)
        self.assertIn("incremental: 'true'", workflow)

    def test_aggregate_sync_commits_manifest_on_drift(self) -> None:
        workflow = (
            REPOSITORY_ROOT / ".github" / "workflows" / "sync-check.yml"
        ).read_text()

        self.assertIn("types: [source-updated]", workflow)
        self.assertIn("git add -A skills .claude-plugin/plugin.json", workflow)

    def write_readme(self, root: Path, skill_paths: list[str]) -> None:
        categories: dict[str, list[str]] = {}
        for skill_path in skill_paths:
            _, category, skill = skill_path.split("/")
            categories.setdefault(category, []).append(skill)

        navigation = []
        for category, folders in TAXONOMY.items():
            skills = [
                (folder, skill)
                for folder in folders
                for skill in categories.get(folder, [])
            ]
            if not skills:
                continue
            navigation.append(f"### {category}")
            navigation.extend(
                f"- [{skill}](skills/{folder}/{skill}/)" for folder, skill in skills
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
            "skills/ai-visibility/ai-visibility-skill",
            "skills/agentic-commerce/agentic-commerce-skill",
            "skills/email-marketing/email-marketing-skill",
            "skills/engineering/engineering-skill",
            "skills/php/php-skill",
            "skills/laravel/laravel-skill",
            "skills/filament/filament-skill",
            "skills/product/product-skill",
            "skills/productivity/productivity-skill",
        ]
        (root / ".claude-plugin" / "plugin.json").write_text(json.dumps({"skills": skill_paths}))
        for skill_path in skill_paths:
            skill_directory = root / skill_path
            skill_directory.mkdir(parents=True)
            (skill_directory / "SKILL.md").write_text("# Example\n")
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
        retired_reference = root / "skills" / "ai-visibility" / "reference.md"
        retired_reference.write_text("\n".join(RETIRED_REPOSITORIES))
        subprocess.run(["git", "add", str(retired_reference.relative_to(root))], cwd=root, check=True)

        result = self.validate(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("former source repos", result.stderr)
        self.assertIn("skills/ai-visibility/reference.md", result.stderr)
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

    def test_rejects_unapproved_source_sync_workflows(self) -> None:
        root = self.make_repository()
        workflow = root / ".github" / "workflows" / "sync-legacy.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text("name: Legacy sync\n")
        subprocess.run(["git", "add", str(workflow.relative_to(root))], cwd=root, check=True)

        result = self.validate(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source-sync automation", result.stderr)
        self.assertIn(".github/workflows/sync-legacy.yml", result.stderr)

    def test_rejects_a_skill_with_missing_check_commands(self) -> None:
        root = self.make_repository()
        skill = root / "skills" / "agentic-commerce" / "agentic-commerce-skill" / "SKILL.md"
        skill.write_text("# Example\n\nRun `references/checks.md`.\n")
        subprocess.run(["git", "add", str(skill.relative_to(root))], cwd=root, check=True)

        result = self.validate(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing check commands", result.stderr)
        self.assertIn(
            "skills/agentic-commerce/agentic-commerce-skill/references/checks.md",
            result.stderr,
        )

    def test_rejects_missing_or_duplicate_skill_navigation(self) -> None:
        root = self.make_repository()
        readme = root / "README.md"
        readme.write_text(
            readme.read_text().replace(
                "- [productivity-skill](skills/productivity/productivity-skill/)\n", ""
            ).replace(
                "- [ai-visibility-skill](skills/ai-visibility/ai-visibility-skill/)\n",
                "- [ai-visibility-skill](skills/ai-visibility/ai-visibility-skill/)\n"
                "- [ai-visibility-skill](skills/ai-visibility/ai-visibility-skill/)\n",
            )
        )
        subprocess.run(["git", "add", "README.md"], cwd=root, check=True)

        result = self.validate(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("README skill navigation", result.stderr)

    def test_rejects_skills_under_the_wrong_taxonomy_category(self) -> None:
        root = self.make_repository()
        readme = root / "README.md"
        engineering_skill = "- [engineering-skill](skills/engineering/engineering-skill/)\n"
        readme.write_text(
            readme.read_text()
            .replace(f"### Engineering Workflow\n{engineering_skill}", "### Engineering Workflow\n")
            .replace("### AI Visibility\n", f"### AI Visibility\n{engineering_skill}")
        )
        subprocess.run(["git", "add", "README.md"], cwd=root, check=True)

        result = self.validate(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("taxonomy category", result.stderr)
