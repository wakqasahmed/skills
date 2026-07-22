#!/usr/bin/env python3
"""Run a versioned event-webinar harness in clean skill-enabled and disabled workspaces."""
import argparse
from collections import Counter
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from evaluate_outcomes import OUTCOME_KEY, PROMPTS, score_records


EVAL = Path(__file__).parent
HARNESS_VERSION = "1"


def validate_records(records: list[dict], cases: list[dict], trials: int) -> None:
    required = {(case["name"], condition, trial) for case in cases for condition in ("enabled", "disabled") for trial in range(trials)}
    keys = [(record.get("name"), record.get("condition"), record.get("trial")) for record in records]
    if set(keys) != required or len(keys) != len(required) or any(count != 1 for count in Counter(keys).values()):
        raise ValueError("harness records must cover every case, condition, and trial exactly once")
    if any(record.get("harness_version") != HARNESS_VERSION for record in records):
        raise ValueError("harness records must declare the supported harness version")
    if any(not isinstance(record.get("outcome"), dict) for record in records):
        raise ValueError("harness records must contain an outcome object")


def score_condition(records: list[dict], condition: str, cases: list[dict], outcomes: dict[str, dict], trials: int) -> int:
    passed = 0
    for trial in range(trials):
        trial_records = [{"name": record["name"], "outcome": record["outcome"]} for record in records if record["condition"] == condition and record["trial"] == trial]
        passed += score_records(trial_records, cases, outcomes)["passed"]
    return passed


def prepare_workspace(workspace: Path, runner: Path, condition: str) -> None:
    shutil.copy2(PROMPTS, workspace / "prompts.json")
    shutil.copy2(runner, workspace / "runner")
    (workspace / "runner").chmod(0o755)
    if condition == "enabled":
        shutil.copy2(EVAL.parent / "SKILL.md", workspace / "SKILL.md")


def isolated_command(workspace: Path, image: str, condition: str, trial: int) -> list[str]:
    return [
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
        "--mount", f"type=bind,source={workspace},target=/workspace,readonly",
        "--env", "HARNESS_WORKSPACE=/workspace",
        "--env", f"HARNESS_CONDITION={condition}",
        "--env", f"HARNESS_TRIAL={trial}",
        "--env", f"HARNESS_VERSION={HARNESS_VERSION}",
        "--workdir", "/workspace", image, "/workspace/runner",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--trials", type=int, choices=range(3, 7), default=3)
    parser.add_argument("--threshold", type=float, default=0.8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not re.search(r"@sha256:[0-9a-f]{64}$", args.image):
        raise SystemExit("image must be pinned by a sha256 digest")
    runner = args.runner.resolve()
    if not runner.is_file() or not runner.is_relative_to(Path.cwd()):
        raise SystemExit("runner must be a repository-controlled file")
    cases = json.loads(PROMPTS.read_text())["cases"]
    outcomes = json.loads(OUTCOME_KEY.read_text())["outcomes"]
    records = []
    for condition in ("enabled", "disabled"):
        for trial in range(args.trials):
            with tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory)
                prepare_workspace(workspace, runner, condition)
                result = subprocess.run(isolated_command(workspace, args.image, condition, trial), text=True, capture_output=True, env={"PATH": os.environ["PATH"], "HOME": "/nonexistent"}, check=True)
                records.extend(json.loads(result.stdout))
    validate_records(records, cases, args.trials)
    total = len(cases) * args.trials
    enabled_passed = score_condition(records, "enabled", cases, outcomes, args.trials)
    disabled_passed = score_condition(records, "disabled", cases, outcomes, args.trials)
    summary = {"enabled_pass_rate": enabled_passed / total, "disabled_pass_rate": disabled_passed / total, "delta": (enabled_passed - disabled_passed) / total, "threshold": args.threshold}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with runner.open("rb") as runner_file:
        runner_sha256 = hashlib.file_digest(runner_file, "sha256").hexdigest()
    args.output.write_text(json.dumps({"harness_version": HARNESS_VERSION, "runner_sha256": runner_sha256, "image": args.image, "trials": args.trials, "summary": summary, "records": records}, indent=2))
    if summary["enabled_pass_rate"] < args.threshold or summary["delta"] <= 0:
        raise SystemExit(f"harness gate failed: {summary}")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
