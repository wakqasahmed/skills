#!/usr/bin/env python3
"""Run a supplied newsletter agent harness in isolated enabled/disabled workspaces."""
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
RUNNER_INPUTS = EVAL / "fixtures" / "runner-inputs.json"
RUNNER_CONTRACT = EVAL / "fixtures" / "runner-output-schema.json"


def validate(
    records: list[dict], cases: list[dict], trials: int, runner_version: str, model: str
) -> dict:
    contract = json.loads(RUNNER_CONTRACT.read_text())
    required_fields = set(contract["required_record_fields"])
    if contract["schema_version"] != 1:
        raise ValueError("unsupported runner output schema")
    for record in records:
        if not required_fields.issubset(record):
            raise ValueError("harness record does not satisfy the versioned runner output schema")
        if record["runner_version"] != runner_version or record["model"] != model:
            raise ValueError("harness record runner version or model does not match the declared run")
    expected = {case["case_id"]: case["expected"] for case in cases}
    required = {
        (name, condition, trial)
        for name in expected
        for condition in ("enabled", "disabled")
        for trial in range(trials)
    }
    keys = [(record.get("case_id"), record.get("condition"), record.get("trial")) for record in records]
    if set(keys) != required or len(keys) != len(required) or any(count != 1 for count in Counter(keys).values()):
        raise ValueError("harness records do not cover every case, condition, and trial exactly once")

    enabled = [record for record in records if record["condition"] == "enabled"]
    disabled = [record for record in records if record["condition"] == "disabled"]
    enabled_passes = sum(record["outcome"] == expected[record["case_id"]] for record in enabled)
    disabled_passes = sum(record["outcome"] == expected[record["case_id"]] for record in disabled)
    return {
        "enabled_pass_rate": enabled_passes / len(enabled),
        "disabled_pass_rate": disabled_passes / len(disabled),
        "delta": (enabled_passes - disabled_passes) / len(enabled),
    }


def prepare_workspace(workspace: Path, runner: Path, condition: str) -> None:
    shutil.copy2(RUNNER_INPUTS, workspace / "cases.json")
    shutil.copy2(runner, workspace / "runner")
    (workspace / "runner").chmod(0o755)
    if condition == "enabled":
        shutil.copy2(EVAL.parent / "SKILL.md", workspace / "SKILL.md")


def isolated_command(
    workspace: Path, image: str, condition: str, trial: int, runner_version: str, model: str
) -> list[str]:
    return [
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
        "--mount", f"type=bind,source={workspace},target=/workspace,readonly",
        "--env", "HARNESS_WORKSPACE=/workspace",
        "--env", f"HARNESS_RUNNER_VERSION={runner_version}",
        "--env", f"HARNESS_MODEL={model}",
        "--workdir", "/workspace", image, "/workspace/runner",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--runner-version", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--trials", type=int, choices=range(3, 7), default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runner = args.runner.resolve()
    if not runner.is_file() or not runner.is_relative_to(Path.cwd()):
        raise SystemExit("runner must be a repository-controlled file")
    if "@sha256:" not in args.image:
        raise SystemExit("image must be pinned by digest")

    cases = json.loads(FIXTURES.read_text())["cases"]
    records = []
    for condition in ("enabled", "disabled"):
        for trial in range(args.trials):
            with tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory)
                prepare_workspace(workspace, runner, condition)
                result = subprocess.run(
                    isolated_command(
                        workspace, args.image, condition, trial, args.runner_version, args.model
                    ),
                    text=True,
                    capture_output=True,
                    env={"PATH": os.environ["PATH"], "HOME": "/nonexistent"},
                    check=True,
                )
                records.extend(
                    {**record, "condition": condition, "trial": trial}
                    for record in json.loads(result.stdout)
                )

    summary = validate(records, cases, args.trials, args.runner_version, args.model)
    if summary["enabled_pass_rate"] < 0.8 or summary["delta"] <= 0:
        raise SystemExit(f"harness gate failed: {summary}")
    args.output.write_text(
        json.dumps(
            {
                "trials": args.trials,
                "runner": str(args.runner),
                "runner_version": args.runner_version,
                "model": args.model,
                "image": args.image,
                "summary": summary,
                "records": records,
            },
            indent=2,
        )
    )
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
