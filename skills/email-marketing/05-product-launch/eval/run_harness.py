#!/usr/bin/env python3
"""Run a declared launch harness in isolated skill-enabled and disabled workspaces."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from evaluate_outcomes import load_cases, validate_records


EVAL = Path(__file__).parent
IMAGE_DIGEST_PATTERN = re.compile(r".+@sha256:[0-9a-f]{64}$")


def validate_image_reference(image: str) -> None:
    if not IMAGE_DIGEST_PATTERN.fullmatch(image):
        raise ValueError("image must be digest-pinned as name@sha256:<64 lowercase hex characters>")


def runner_metadata(runner: Path) -> dict[str, str]:
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=Path.cwd(),
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    return {
        "runner_revision": revision,
        "runner_sha256": hashlib.sha256(runner.read_bytes()).hexdigest(),
    }


def prepare_workspace(workspace: Path, runner: Path, condition: str, cases: list[dict]) -> None:
    public_cases = {"schema_version": 1, "cases": [{"name": case["name"], "prompt": case["prompt"]} for case in cases]}
    (workspace / "cases.json").write_text(json.dumps(public_cases))
    shutil.copy2(runner, workspace / "runner")
    (workspace / "runner").chmod(0o755)
    if condition == "enabled":
        shutil.copy2(EVAL.parent / "SKILL.md", workspace / "SKILL.md")


def isolated_command(workspace: Path, image: str, trial: int, model: str, harness_version: str) -> list[str]:
    return [
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
        "--mount", f"type=bind,source={workspace},target=/workspace,readonly",
        "--env", "HARNESS_WORKSPACE=/workspace",
        "--env", f"HARNESS_TRIAL={trial}",
        "--env", f"HARNESS_MODEL={model}",
        "--env", f"HARNESS_VERSION={harness_version}",
        "--workdir", "/workspace", image, "/workspace/runner",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--harness-version", required=True)
    parser.add_argument("--trials", type=int, choices=range(3, 7), default=3)
    parser.add_argument("--pass-rate-threshold", type=float, default=.8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 0 < args.pass_rate_threshold <= 1:
        raise SystemExit("pass-rate threshold must be greater than 0 and at most 1")
    try:
        validate_image_reference(args.image)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    runner = args.runner.resolve()
    if not runner.is_file() or not runner.is_relative_to(Path.cwd()):
        raise SystemExit("runner must be a repository-controlled file")
    cases, fixture_failures = load_cases()
    if fixture_failures:
        raise SystemExit("invalid held-out fixtures: " + "; ".join(fixture_failures))

    records = []
    for condition in ("enabled", "disabled"):
        for trial in range(args.trials):
            with tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory)
                prepare_workspace(workspace, runner, condition, cases)
                result = subprocess.run(
                    isolated_command(workspace, args.image, trial, args.model, args.harness_version),
                    text=True,
                    capture_output=True,
                    env={"PATH": os.environ["PATH"], "HOME": "/nonexistent"},
                    check=True,
                )
                outcomes = json.loads(result.stdout)
                records.extend({
                    "name": outcome.get("name"),
                    "condition": condition,
                    "trial": trial,
                    "outcome": outcome.get("outcome"),
                } for outcome in outcomes)

    failures, summary = validate_records(records, cases, args.trials)
    if failures:
        raise SystemExit("harness gate failed: " + "; ".join(failures))
    if summary["enabled_pass_rate"] < args.pass_rate_threshold or summary["delta"] <= 0:
        raise SystemExit(f"harness gate failed: {summary}")

    args.output.write_text(json.dumps({
        "image_digest": args.image,
        "model": args.model,
        "harness_version": args.harness_version,
        **runner_metadata(runner),
        "trials": args.trials,
        "pass_rate_threshold": args.pass_rate_threshold,
        "summary": summary,
        "records": records,
    }, indent=2))
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
