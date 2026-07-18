#!/usr/bin/env python3
"""Run a user-supplied agent harness in isolated skill-enabled/disabled workspaces."""
import argparse
from collections import Counter
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


EVAL = Path(__file__).parent
FIXTURES = EVAL / "fixtures" / "held-out-scenarios.json"


def validate(records: list[dict], cases: list[dict], trials: int) -> dict:
    expected = {case["name"]: case["expected"] for case in cases}
    required = {(name, condition, trial) for name in expected for condition in ("enabled", "disabled") for trial in range(trials)}
    actual = {(r.get("name"), r.get("condition"), r.get("trial")) for r in records}
    if actual != required:
        raise ValueError("harness records do not cover every case, condition, and trial exactly once")
    record_keys = [(r.get("name"), r.get("condition"), r.get("trial")) for r in records]
    if len(records) != len(required) or any(count != 1 for count in Counter(record_keys).values()):
        raise ValueError("harness records do not cover every case, condition, and trial exactly once")
    enabled = [r for r in records if r["condition"] == "enabled"]
    enabled_passes = sum(r["outcome"] == expected[r["name"]] for r in enabled)
    disabled_passes = sum(r["outcome"] == expected[r["name"]] for r in records if r["condition"] == "disabled")
    return {"enabled_pass_rate": enabled_passes / len(enabled), "disabled_pass_rate": disabled_passes / (len(records) - len(enabled)), "delta": (enabled_passes - disabled_passes) / len(enabled)}


def prepare_workspace(workspace: Path, runner: Path, condition: str) -> None:
    shutil.copy2(FIXTURES, workspace / "cases.json")
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
        "--workdir", "/workspace", image, "/workspace/runner",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--trials", type=int, choices=range(3, 7), default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runner = args.runner.resolve()
    if not runner.is_file() or not runner.is_relative_to(Path.cwd()):
        raise SystemExit("runner must be a repository-controlled file")
    cases = json.loads(FIXTURES.read_text())["cases"]
    records = []
    for condition in ("enabled", "disabled"):
        for trial in range(args.trials):
            with tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory)
                prepare_workspace(workspace, runner, condition)
                result = subprocess.run(isolated_command(workspace, args.image, condition, trial), text=True, capture_output=True, env={"PATH": os.environ["PATH"], "HOME": "/nonexistent"}, check=True)
                records.extend(json.loads(result.stdout))
    summary = validate(records, cases, args.trials)
    if summary["enabled_pass_rate"] < .8 or summary["delta"] <= 0:
        raise SystemExit(f"harness gate failed: {summary}")
    args.output.write_text(json.dumps({"trials": args.trials, "summary": summary, "records": records}, indent=2))
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
