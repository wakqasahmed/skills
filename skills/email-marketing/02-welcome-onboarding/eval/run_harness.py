#!/usr/bin/env python3
"""Run a user-supplied agent in isolated welcome-onboarding eval workspaces."""
import argparse
from collections import Counter
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


EVAL = Path(__file__).parent
FIXTURES = EVAL / "fixtures" / "held-out-scenarios.json"


def require_digest_pinned_image(image: str) -> None:
    digest = image.rsplit("@sha256:", 1)[-1]
    if "@sha256:" not in image or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("image must be digest-pinned with @sha256:<64-hex-digest>")


def validate(records: list[dict], cases: list[dict], trials: int) -> dict:
    expected = {case["name"]: case["expected_outcome"] for case in cases}
    required = {
        (name, condition, trial)
        for name in expected
        for condition in ("enabled", "disabled")
        for trial in range(trials)
    }
    keys = [(record.get("name"), record.get("condition"), record.get("trial")) for record in records]
    if set(keys) != required or len(records) != len(required) or any(count != 1 for count in Counter(keys).values()):
        raise ValueError("harness records do not cover every case, condition, and trial exactly once")

    enabled = [record for record in records if record["condition"] == "enabled"]
    disabled = [record for record in records if record["condition"] == "disabled"]
    enabled_passes = sum(record["outcome"] == expected[record["name"]] for record in enabled)
    disabled_passes = sum(record["outcome"] == expected[record["name"]] for record in disabled)
    return {
        "enabled_pass_rate": enabled_passes / len(enabled),
        "disabled_pass_rate": disabled_passes / len(disabled),
        "delta": (enabled_passes - disabled_passes) / len(enabled),
    }


def prepare_workspace(workspace: Path, runner: Path, condition: str) -> None:
    cases = json.loads(FIXTURES.read_text())["cases"]
    blinded = {
        "schema_version": 1,
        "cases": [{"name": case["name"], "prompt": case["prompt"]} for case in cases],
    }
    (workspace / "cases.json").write_text(json.dumps(blinded, indent=2))
    shutil.copy2(runner, workspace / "runner")
    (workspace / "runner").chmod(0o755)
    if condition == "enabled":
        shutil.copy2(EVAL.parent / "SKILL.md", workspace / "SKILL.md")


def isolated_command(workspace: Path, image: str, version: str) -> list[str]:
    return [
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
        "--mount", f"type=bind,source={workspace},target=/workspace,readonly",
        "--env", "HOME=/nonexistent",
        "--env", "HARNESS_WORKSPACE=/workspace",
        "--env", f"HARNESS_VERSION={version}",
        "--workdir", "/workspace", image, "/workspace/runner",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--trials", type=int, choices=range(3, 7), default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runner = args.runner.resolve()
    if not runner.is_file() or not runner.is_relative_to(Path.cwd()):
        raise SystemExit("runner must be a repository-controlled file")
    try:
        require_digest_pinned_image(args.image)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    cases = json.loads(FIXTURES.read_text())["cases"]
    records = []
    for condition in ("enabled", "disabled"):
        for trial in range(args.trials):
            with tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory)
                prepare_workspace(workspace, runner, condition)
                result = subprocess.run(
                    isolated_command(workspace, args.image, args.version),
                    text=True,
                    capture_output=True,
                    env={"PATH": os.environ["PATH"], "HOME": "/nonexistent"},
                    check=True,
                )
                records.extend(
                    {**record, "condition": condition, "trial": trial}
                    for record in json.loads(result.stdout)
                )
    summary = validate(records, cases, args.trials)
    args.output.write_text(json.dumps({"version": args.version, "image": args.image, "trials": args.trials, "summary": summary, "records": records}, indent=2))
    if summary["enabled_pass_rate"] < 0.8 or summary["delta"] <= 0:
        raise SystemExit(f"harness gate failed: {summary}")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
