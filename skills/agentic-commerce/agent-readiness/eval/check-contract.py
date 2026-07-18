#!/usr/bin/env python3
"""Separate deterministic checks for agent-readiness non-negotiable instructions."""
import json
from pathlib import Path


def main() -> int:
    eval_dir = Path(__file__).parent
    skill = (eval_dir.parent / "SKILL.md").read_text().casefold()
    required = ("separate read readiness from action readiness", "explicit blocker codes", "do not call an action safe")
    missing = [phrase for phrase in required if phrase not in skill]
    if missing:
        print("missing contract phrases: " + ", ".join(missing))
        return 1
    cases = json.loads((eval_dir / "fixtures" / "held-out.json").read_text())["cases"]
    required = {"id", "split", "prompt", "expected_skill_usage", "expected_outcome", "expected_safety_outcome"}
    if len(cases) < 10 or any(case["split"] != "held_out" or required - case.keys() for case in cases):
        print("held-out fixture contract failed")
        return 1
    print("PASS agent-readiness contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
