import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "eval" / "run-trigger-evals.py"
CASES = ROOT / "eval" / "trigger-cases.json"


def load_runner():
    spec = importlib.util.spec_from_file_location("trigger_evals", RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TriggerEvalTest(unittest.TestCase):
    def test_every_skill_has_a_realistic_positive_and_near_miss(self):
        data = json.loads(CASES.read_text())
        discovered = {str(path.parent.relative_to(ROOT / "skills")) for path in (ROOT / "skills").glob("*/*/SKILL.md")}
        self.assertEqual({case["skill"] for case in data["cases"]}, discovered)
        self.assertEqual(len(data["cases"]), len(discovered))
        self.assertEqual({case["category"] for case in data["cases"]}, set(data["minimum_metrics"]))
        for case in data["cases"]:
            self.assertTrue(case["positive"])
            self.assertTrue(case["negative"])
            self.assertIn(case["split"], {"train", "validation"})

    def test_train_and_validation_use_disjoint_complete_examples(self):
        runner = load_runner()
        cases = json.loads(CASES.read_text())["cases"]
        train = runner.cases_for_split(cases, "train")
        validation = runner.cases_for_split(cases, "validation")

        self.assertTrue(train)
        self.assertTrue(validation)
        self.assertTrue(all(case["split"] == "train" for case in train))
        self.assertTrue(all(case["split"] == "validation" for case in validation))
        self.assertTrue({case["skill"] for case in train}.isdisjoint({case["skill"] for case in validation}))
        self.assertEqual(
            {(case["skill"], prompt) for case in train for prompt in (case["positive"], case["negative"])},
            {(case["skill"], prompt) for case in cases if case["split"] == "train" for prompt in (case["positive"], case["negative"])},
        )

    def test_routing_uses_the_checked_in_skill_description(self):
        runner = load_runner()
        case = next(case for case in json.loads(CASES.read_text())["cases"] if case["skill"] == "ai-visibility/ai-visibility-audit")
        description = runner.skill_description(case["skill"], ROOT)
        self.assertTrue(runner.matches(case["positive"], description))

        with tempfile.TemporaryDirectory() as directory:
            fixture_root = Path(directory)
            skill_path = fixture_root / "skills" / case["skill"] / "SKILL.md"
            skill_path.parent.mkdir(parents=True)
            skill_path.write_text("---\nname: unrelated\ndescription: Schedule a garden party.\n---\n")
            self.assertFalse(runner.matches(case["positive"], runner.skill_description(case["skill"], fixture_root)))

    def test_evaluation_counts_other_routed_skills_as_false_positives(self):
        runner = load_runner()
        cases = [{
            "skill": "category/target",
            "category": "test",
            "positive": "Route this database migration safely.",
            "negative": "Arrange a garden party.",
            "split": "validation",
        }]

        with tempfile.TemporaryDirectory() as directory:
            fixture_root = Path(directory)
            for skill in ("category/target", "category/other"):
                skill_path = fixture_root / "skills" / skill / "SKILL.md"
                skill_path.parent.mkdir(parents=True, exist_ok=True)
                skill_path.write_text(
                    f"---\nname: {skill.rsplit('/', 1)[1]}\n"
                    "description: Route database migration safely.\n---\n"
                )

            self.assertEqual(
                runner.evaluate(cases, "validation", fixture_root),
                {"test": {"tp": 1, "fp": 1, "fn": 0}},
            )

    def test_runner_passes_train_and_validation_without_network(self):
        for split in ("train", "validation"):
            result = subprocess.run(["python3", str(RUNNER), "--split", split], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("precision=1.00 recall=1.00", result.stdout)
