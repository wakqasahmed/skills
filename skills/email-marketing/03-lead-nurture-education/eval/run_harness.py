#!/usr/bin/env python3
"""Run a supplied agent runner in clean, isolated skill ablation workspaces."""
import argparse
from collections import Counter
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


EVAL = Path(__file__).parent
PROMPTS = EVAL / "fixtures" / "held-out-prompts.json"
KEYS = EVAL / "fixtures" / "scoring-key.json"
THRESHOLD = 0.8


def matches(outcome: dict, expected: dict) -> bool:
    return outcome.get("decision") == expected["decision"] and set(expected["required_actions"]).issubset(outcome.get("actions", []))


def validate(records: list[dict], keys: dict, trials: int) -> dict:
    expected = keys["outcomes"]
    required = {(name, condition, trial) for name in expected for condition in ("enabled", "disabled") for trial in range(trials)}
    record_keys = [(record.get("name"), record.get("condition"), record.get("trial")) for record in records]
    if set(record_keys) != required or len(records) != len(required) or any(count != 1 for count in Counter(record_keys).values()):
        raise ValueError("harness records must cover every case, condition, and trial exactly once")
    scores = {}
    for condition in ("enabled", "disabled"):
        condition_records = [record for record in records if record["condition"] == condition]
        scores[condition] = sum(matches(record.get("outcome", {}), expected[record["name"]]) for record in condition_records) / len(condition_records)
    return {"enabled_pass_rate": scores["enabled"], "disabled_pass_rate": scores["disabled"], "delta": scores["enabled"] - scores["disabled"]}


def prepare_workspace(workspace: Path, runner: Path, condition: str) -> None:
    shutil.copy2(PROMPTS, workspace / "cases.json")
    shutil.copy2(runner, workspace / "runner")
    (workspace / "runner").chmod(0o755)
    if condition == "enabled":
        shutil.copy2(EVAL.parent / "SKILL.md", workspace / "SKILL.md")


def isolated_command(workspace: Path, image: str, condition: str, trial: int) -> list[str]:
    return [
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
        "--mount", f"type=bind,source={workspace},target=/workspace,readonly",
        "--env", "HOME=/nonexistent",
        "--env", "HARNESS_WORKSPACE=/workspace",
        "--env", f"HARNESS_CONDITION={condition}",
        "--env", f"HARNESS_TRIAL={trial}",
        "--workdir", "/workspace", image, "/workspace/runner",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--harness-version", required=True)
    parser.add_argument("--trials", type=int, choices=range(3, 7), default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if "@sha256:" not in args.image:
        raise SystemExit("image must be digest-pinned")
    runner = args.runner.resolve()
    if not runner.is_file() or not runner.is_relative_to(Path.cwd()):
        raise SystemExit("runner must be a repository-controlled executable")
    keys = json.loads(KEYS.read_text())
    records = []
    for condition in ("enabled", "disabled"):
        for trial in range(args.trials):
            with tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory)
                prepare_workspace(workspace, runner, condition)
                result = subprocess.run(isolated_command(workspace, args.image, condition, trial), text=True, capture_output=True, env={"PATH": os.environ["PATH"]}, check=True)
                records.extend(json.loads(result.stdout))
    summary = validate(records, keys, args.trials)
    if summary["enabled_pass_rate"] < THRESHOLD or summary["delta"] <= 0:
        raise SystemExit(f"harness gate failed: {summary}")
    args.output.write_text(json.dumps({"schema_version": 1, "model": args.model, "harness_version": args.harness_version, "image": args.image, "trials": args.trials, "threshold": THRESHOLD, "summary": summary, "records": records}, indent=2))
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
