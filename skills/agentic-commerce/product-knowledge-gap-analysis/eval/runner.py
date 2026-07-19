#!/usr/bin/env python3
"""Repository-controlled adapter for the pinned offline target image."""
import json
import os
import subprocess
from pathlib import Path


PROTOCOL_VERSION = "product-knowledge-outcome-runner/v2"
TARGET = "/usr/local/bin/product-knowledge-target"
TARGET_TIMEOUT_SECONDS = 30


def main() -> int:
    workspace = Path(os.environ["HARNESS_WORKSPACE"])
    request = json.loads((workspace / "case.json").read_text())
    skill = workspace / "SKILL.md"
    request["skill"] = skill.read_text() if skill.exists() else None
    result = subprocess.run(
        [TARGET, "--model", os.environ["HARNESS_MODEL"]],
        input=json.dumps(request), text=True, capture_output=True, check=True,
        timeout=TARGET_TIMEOUT_SECONDS,
    )
    artifact = json.loads(result.stdout)
    if not isinstance(artifact, dict):
        raise SystemExit("target must emit one artifact object")
    print(json.dumps({"protocol_version": PROTOCOL_VERSION, "artifact": artifact}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
