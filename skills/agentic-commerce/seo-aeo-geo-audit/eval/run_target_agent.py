#!/usr/bin/env python3
"""Adapter for the target agent baked into the pinned evaluator image."""
import json
import os
import subprocess
from pathlib import Path


PROTOCOL_VERSION = "seo-aeo-geo-artifact-runner/v1"
DEFAULT_TARGET_AGENT = "/usr/local/bin/seo-aeo-geo-audit-agent"


def workspace_request(workspace: Path, condition: str, model: str) -> dict:
    case = json.loads((workspace / "case.json").read_text())
    request = {
        "protocol_version": PROTOCOL_VERSION,
        "model": model,
        "condition": condition,
        "prompt": case["prompt"],
        "input": case["input"],
    }
    if condition == "enabled":
        request["skill"] = (workspace / "SKILL.md").read_text()
        request["checks"] = (workspace / "checks.md").read_text()
    return request


def run_target_agent(request: dict, command: str) -> dict:
    result = subprocess.run(
        [command, "--model", request["model"]],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        check=True,
    )
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise SystemExit(f"target agent must emit one JSON object: {error}") from error
    if not isinstance(response, dict):
        raise SystemExit("target agent must emit one JSON object")
    return response


def main() -> int:
    workspace = Path(os.environ.get("HARNESS_WORKSPACE", "/workspace"))
    condition = os.environ["HARNESS_CONDITION"]
    model = os.environ["HARNESS_MODEL"]
    response = run_target_agent(
        workspace_request(workspace, condition, model),
        os.environ.get("TARGET_AGENT_COMMAND", DEFAULT_TARGET_AGENT),
    )
    if response.get("model") != model or not isinstance(response.get("model_version"), str) or not response["model_version"].strip():
        raise SystemExit("target agent must attest the requested model and a non-empty model_version")
    if not isinstance(response.get("skill_used"), bool) or not isinstance(response.get("audit_artifact"), dict):
        raise SystemExit("target agent must emit skill_used and an audit_artifact object")
    print(json.dumps({
        "protocol_version": PROTOCOL_VERSION,
        "model": response["model"],
        "model_version": response["model_version"],
        "skill_used": response["skill_used"],
        "audit_artifact": response["audit_artifact"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
