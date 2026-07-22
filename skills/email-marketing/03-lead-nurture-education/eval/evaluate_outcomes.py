#!/usr/bin/env python3
"""Score frozen lead-nurture outcomes against a separately held scoring key."""
import json
from pathlib import Path


EVAL = Path(__file__).parent
PROMPTS = EVAL / "fixtures" / "held-out-prompts.json"
KEYS = EVAL / "fixtures" / "scoring-key.json"
CANDIDATES = EVAL / "fixtures" / "candidate-outcomes.json"


def score(candidates: dict, keys: dict) -> tuple[int, int, list[str]]:
    failures = []
    for name, expected in keys.items():
        actual = candidates.get(name)
        if not isinstance(actual, dict):
            failures.append(f"{name}: missing outcome")
            continue
        if actual.get("decision") != expected["decision"]:
            failures.append(f"{name}: decision")
            continue
        if not set(expected["required_actions"]).issubset(actual.get("actions", [])):
            failures.append(f"{name}: required actions")
    return len(keys) - len(failures), len(keys), failures


def main() -> int:
    prompts = json.loads(PROMPTS.read_text())
    keys = json.loads(KEYS.read_text())
    candidates = json.loads(CANDIDATES.read_text())
    cases = prompts["cases"]
    names = {case["name"] for case in cases}
    if len(cases) < 10 or names != set(keys["outcomes"]) or names != set(candidates["outcomes"]):
        raise SystemExit("FAIL: held-out prompt, scoring-key, and candidate-outcome names must match (minimum 10)")
    if any("expected" in case or "outcome" in case for case in cases):
        raise SystemExit("FAIL: held-out prompts must not contain scoring answers")
    passed, total, failures = score(candidates["outcomes"], keys["outcomes"])
    if failures:
        raise SystemExit("FAIL: outcome score " + ", ".join(failures))
    print(f"PASS: outcome score {passed}/{total} held-out lead-nurture cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
