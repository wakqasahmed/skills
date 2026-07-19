# Readiness-audit outcome eval

`python3 run.py` is the credential-free, offline PR-CI layer. It checks frozen held-out fixture coverage and non-negotiable SKILL.md contract text; it does not generate or grade an agent response.

The gated `run_harness.py` runs five enabled and disabled trials per case. Each trial has a fresh disposable workspace containing only its prompt, frozen HTML fixture, repository-controlled runner, and SKILL.md only when enabled. It uses a digest-pinned, read-only container with no network, empty home, and no inherited credentials. The runner emits activation telemetry and the target response; `validate-harness-results.py` independently grades fixture-grounded outcome and safety evidence. Enabled cases require 80% activation and outcome pass rates, no enabled safety misses, and at least a 2% enabled activation/outcome advantage. Results retain model, runner protocol, harness version, condition, and trial metadata.
