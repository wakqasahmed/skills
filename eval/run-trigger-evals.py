#!/usr/bin/env python3
"""Run deterministic should-trigger routing checks without network access."""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "eval" / "trigger-cases.json"


def matches(text: str, terms: list[str]) -> bool:
    normalized = text.casefold()
    return all(term.casefold() in normalized for term in terms)


def discovered_skills(root: Path) -> set[str]:
    return {str(path.parent.relative_to(root / "skills")) for path in (root / "skills").glob("*/*/SKILL.md")}


def evaluate(cases: list[dict], split: str) -> dict[str, dict[str, int]]:
    metrics: dict[str, dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    for index, case in enumerate(cases):
        category = case["category"]
        positive_split = "train" if index % 2 == 0 else "validation"
        negative_split = "validation" if positive_split == "train" else "train"
        for expected, text, case_split in (
            (True, case["positive"], positive_split),
            (False, case["negative"], negative_split),
        ):
            if split != "all" and split != case_split:
                continue
            actual = matches(text, case["terms"])
            if actual and expected:
                metrics[category]["tp"] += 1
            elif actual:
                metrics[category]["fp"] += 1
            elif expected:
                metrics[category]["fn"] += 1
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
        missing = sorted(expected - actual)
        stale = sorted(actual - expected)
        print(f"coverage mismatch; missing={missing}; stale={stale}", file=sys.stderr)
        return 1
    if len(cases) != len(actual):
        print("each skill must have exactly one trigger case definition", file=sys.stderr)
        return 1

    thresholds = data["minimum_metrics"]
    metrics = evaluate(cases, arguments.split)
    failed = False
    for category in sorted(metrics):
        counts = metrics[category]
        precision = counts["tp"] / (counts["tp"] + counts["fp"]) if counts["tp"] + counts["fp"] else 0
        recall = counts["tp"] / (counts["tp"] + counts["fn"]) if counts["tp"] + counts["fn"] else 0
        print(f"{category}: precision={precision:.2f} recall={recall:.2f} (tp={counts['tp']}, fp={counts['fp']}, fn={counts['fn']})")
        threshold = thresholds[category]
        failed |= precision < threshold["precision"] or recall < threshold["recall"]
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
