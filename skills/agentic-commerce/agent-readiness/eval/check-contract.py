#!/usr/bin/env python3
"""Separate deterministic checks for agent-readiness non-negotiable instructions."""
from pathlib import Path


def main() -> int:
    skill = (Path(__file__).parent.parent / "SKILL.md").read_text().casefold()
    required = ("separate read readiness from action readiness", "explicit blocker codes", "do not call an action safe")
    missing = [phrase for phrase in required if phrase not in skill]
    if missing:
        print("missing contract phrases: " + ", ".join(missing))
        return 1
    print("PASS agent-readiness contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
