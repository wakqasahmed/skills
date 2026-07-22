#!/usr/bin/env python3
"""Adapter for an approved offline promotional-offer agent in the harness image."""
import json
import subprocess


MODEL_COMMAND = "/usr/local/bin/promotional-offer-agent"
MODEL_VERSION = "promotional-offer-agent-v1"
HARNESS_VERSION = "promotional-offer-runner-v1"


def main() -> int:
    result = subprocess.run(
        [MODEL_COMMAND, "/workspace/cases.json"],
        text=True,
        capture_output=True,
        check=True,
    )
    print(json.dumps({
        "metadata": {
            "model_version": MODEL_VERSION,
            "harness_version": HARNESS_VERSION,
        },
        "records": json.loads(result.stdout),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
