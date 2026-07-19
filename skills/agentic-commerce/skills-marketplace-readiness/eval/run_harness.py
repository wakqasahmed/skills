#!/usr/bin/env python3
"""Run the checked-in marketplace-readiness target-agent contract in isolation."""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


EVAL_DIR = Path(__file__).resolve().parent
CASES = EVAL_DIR / "held-out-cases.json"
FIXTURES = EVAL_DIR / "fixtures" / "repos"
TARGET_RUNNER = EVAL_DIR / "target_agent_runner.py"
HARNESS_VERSION = "2"
RUNNER_PROTOCOL_VERSION = "marketplace-readiness-agent-runner/v2"


def prepare_workspace(workspace: Path, case: dict, condition: str) -> None:
    shutil.copytree(FIXTURES / case["fixture"], workspace / "repository")
    (workspace / "request.json").write_text(json.dumps({"prompt": case["prompt"], "artifact_path": "/tmp/outcome.json"}))
    shutil.copy2(TARGET_RUNNER, workspace / "target_agent_runner.py")
    if condition == "enabled":
        shutil.copy2(EVAL_DIR.parent / "SKILL.md", workspace / "SKILL.md")


def isolated_command(workspace: Path, image: str, model: str, condition: str, trial: int) -> list[str]:
    return [
        "docker", "run", "--rm", "--network", "none", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
        "--mount", f"type=bind,source={workspace},target=/workspace,readonly",
        "--env", "HOME=/nonexistent", "--env", "HARNESS_WORKSPACE=/workspace",
        "--env", f"HARNESS_MODEL={model}", "--env", f"HARNESS_CONDITION={condition}",
        "--env", f"HARNESS_TRIAL={trial}", "--workdir", "/workspace", image,
        "python3", "/workspace/target_agent_runner.py",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--trials", type=int, choices=range(3, 7), default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if "@sha256:" not in args.image:
        raise SystemExit("image must be pinned by digest")
    records = []
    for case in json.loads(CASES.read_text())["cases"]:
        for condition in ("enabled", "disabled"):
            for trial in range(1, args.trials + 1):
                with tempfile.TemporaryDirectory() as directory:
                    prepare_workspace(Path(directory), case, condition)
                    result = subprocess.run(
                        isolated_command(Path(directory), args.image, args.model, condition, trial),
                        text=True, capture_output=True, check=True,
                        env={"PATH": os.environ["PATH"], "HOME": "/nonexistent"},
                    )
                try:
                    artifact = json.loads(result.stdout)
                except json.JSONDecodeError as error:
                    raise SystemExit(f"target agent must emit one JSON artifact: {error}") from error
                records.append({
                    "case_id": case["id"], "condition": condition, "trial": trial,
                    "model": args.model, "harness_version": HARNESS_VERSION,
                    "runner_protocol_version": RUNNER_PROTOCOL_VERSION, "outcome_artifact": artifact,
                })
    args.output.write_text(json.dumps(records, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
