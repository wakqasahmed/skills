#!/usr/bin/env python3
"""Run readiness-audit cases in clean, network-isolated workspaces."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
ROOT = EVAL_DIR.parents[3]
CASES = EVAL_DIR / "held-out-cases.json"
HARNESS_VERSION = "1"
RUNNER_PROTOCOL_VERSION = "readiness-audit-runner/v2"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_workspace(workspace: Path, case: dict, condition: str) -> dict:
    (workspace / "case.json").write_text(json.dumps({"id": case["id"], "prompt": case["prompt"]}))
    shutil.copy2(EVAL_DIR / case["fixture"], workspace / "fixture.html")
    if condition == "enabled":
        shutil.copy2(EVAL_DIR.parent / "SKILL.md", workspace / "SKILL.md")
    files = ["case.json", "fixture.html", *(["SKILL.md"] if condition == "enabled" else [])]
    check = {"protocol_version": RUNNER_PROTOCOL_VERSION, "files": files, "sha256": {name: digest(workspace / name) for name in files}}
    (workspace / "input-check.json").write_text(json.dumps(check))
    return check


def isolated_command(workspace: Path, runner: Path, image: str, model: str, condition: str, trial: int) -> list[str]:
    return [
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
        "--mount", f"type=bind,source={runner},target=/runner,readonly",
        "--mount", f"type=bind,source={workspace / 'case.json'},target=/inputs/case.json,readonly",
        "--mount", f"type=bind,source={workspace / 'fixture.html'},target=/inputs/fixture.html,readonly",
        "--mount", f"type=bind,source={workspace / 'input-check.json'},target=/inputs/input-check.json,readonly",
        *(["--mount", f"type=bind,source={workspace / 'SKILL.md'},target=/inputs/SKILL.md,readonly"] if condition == "enabled" else []),
        "--env", "HOME=/nonexistent",
        "--env", "HARNESS_FIXTURE=/inputs/fixture.html", "--env", f"HARNESS_MODEL={model}",
        "--env", f"HARNESS_CONDITION={condition}", "--env", f"HARNESS_TRIAL={trial}",
        "--workdir", "/tmp", image, "/runner",
        "--case", "/inputs/case.json", "--fixture", "/inputs/fixture.html",
        "--check", "/inputs/input-check.json",
        *(["--skill", "/inputs/SKILL.md"] if condition == "enabled" else []),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--runner-sha256", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--trials", type=int, choices=range(3, 7), default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runner = args.runner.resolve()
    if not runner.is_file() or runner.is_relative_to(ROOT):
        raise SystemExit("runner must be an approved external file")
    if len(args.runner_sha256) != 64 or digest(runner) != args.runner_sha256:
        raise SystemExit("runner must match the declared SHA-256")
    if "@sha256:" not in args.image:
        raise SystemExit("image must be pinned by digest")

    records = []
    for case in json.loads(CASES.read_text())["cases"]:
        for condition in ("enabled", "disabled"):
            for trial in range(1, args.trials + 1):
                with tempfile.TemporaryDirectory() as directory:
                    workspace = Path(directory)
                    input_check = prepare_workspace(workspace, case, condition)
                    result = subprocess.run(isolated_command(workspace, runner, args.image, args.model, condition, trial), text=True, capture_output=True, check=True, timeout=300, env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": "/nonexistent"})
                try:
                    record = json.loads(result.stdout)
                except json.JSONDecodeError as error:
                    raise SystemExit(f"runner must emit one JSON object per case/trial: {error}") from error
                if not isinstance(record, dict) or record.get("protocol_version") != RUNNER_PROTOCOL_VERSION:
                    raise SystemExit(f"runner must use {RUNNER_PROTOCOL_VERSION}")
                if not isinstance(record.get("target_response"), str) or not record["target_response"].strip():
                    raise SystemExit("runner must emit a non-empty target_response")
                records.append({"case_id": case["id"], "condition": condition, "trial": trial, "model": args.model, "harness_version": HARNESS_VERSION, "runner_protocol_version": RUNNER_PROTOCOL_VERSION, "execution": {"exit_code": result.returncode, "image": args.image, "runner_sha256": args.runner_sha256, "provided_inputs": input_check}, "target_response": record["target_response"]})
    args.output.write_text(json.dumps(records, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
