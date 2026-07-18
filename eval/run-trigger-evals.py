#!/usr/bin/env python3
"""Evaluate skill-description routing with a deterministic offline scorer."""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "eval" / "trigger-cases.json"
STOP_WORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "before", "by", "can", "for", "from",
    "after", "form", "in", "into", "is", "it", "of", "on", "or", "our", "run", "that", "the", "this", "to", "use", "when",
    "with", "whether", "your",
})


def skill_description(skill: str, root: Path = ROOT) -> str:
    content = (root / "skills" / skill / "SKILL.md").read_text()
    match = re.search(r"^description:\s*(.+)$", content, re.MULTILINE)
    if match is None:
        raise ValueError(f"missing description for {skill}")
    return match.group(1)


def terms(text: str) -> set[str]:
    return {
        term
        for term in re.findall(r"[a-z0-9]+", text.casefold())
        if len(term) > 2 and term not in STOP_WORDS
    }


def matches(prompt: str, description: str) -> bool:
    """Require two meaningful prompt words from the real SKILL.md description."""
    return score(prompt, description) >= 2


def score(prompt: str, description: str) -> int:
    return len(terms(prompt) & terms(description))


def discovered_skills(root: Path) -> set[str]:
    return {str(path.parent.relative_to(root / "skills")) for path in (root / "skills").glob("*/*/SKILL.md")}


def cases_for_split(cases: list[dict], split: str) -> list[dict]:
    return cases if split == "all" else [case for case in cases if case["split"] == split]


def routed_skills(prompt: str, descriptions: dict[str, str]) -> set[str]:
    scores = {skill: score(prompt, description) for skill, description in descriptions.items()}
    highest_score = max(scores.values(), default=0)
    if highest_score < 2:
        return set()
    return {skill for skill, value in scores.items() if value == highest_score}


def evaluate(cases: list[dict], split: str, root: Path = ROOT) -> dict[str, dict[str, int]]:
    metrics: dict[str, dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    descriptions = {skill: skill_description(skill, root) for skill in discovered_skills(root)}
    for case in cases_for_split(cases, split):
        counts = metrics[case["category"]]
        positive_routes = routed_skills(case["positive"], descriptions)
        if case["skill"] in positive_routes:
            counts["tp"] += 1
        else:
            counts["fn"] += 1
        counts["fp"] += len(positive_routes - {case["skill"]})
        counts["fp"] += len(routed_skills(case["negative"], descriptions))
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--split", choices=("all", "train", "validation"), default="all")
    arguments = parser.parse_args()
    data = json.loads(arguments.cases.read_text())
    cases = data["cases"]
    expected = discovered_skills(ROOT)
    actual = {case["skill"] for case in cases}
    if actual != expected:
        print(f"coverage mismatch; missing={sorted(expected - actual)}; stale={sorted(actual - expected)}", file=sys.stderr)
        return 1
    if len(cases) != len(actual) or {case.get("split") for case in cases} != {"train", "validation"}:
        print("each skill needs one case assigned to either train or validation", file=sys.stderr)
        return 1

    thresholds = data["minimum_metrics"]
    metrics = evaluate(cases, arguments.split)
    failed = False
    for category in sorted(thresholds):
        counts = metrics[category]
        precision = counts["tp"] / (counts["tp"] + counts["fp"]) if counts["tp"] + counts["fp"] else 0
        recall = counts["tp"] / (counts["tp"] + counts["fn"]) if counts["tp"] + counts["fn"] else 0
        print(f"{category}: precision={precision:.2f} recall={recall:.2f} (tp={counts['tp']}, fp={counts['fp']}, fn={counts['fn']})")
        threshold = thresholds[category]
        failed |= precision < threshold["precision"] or recall < threshold["recall"]
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
