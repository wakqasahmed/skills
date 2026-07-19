# Readiness-audit outcome eval

`python3 run.py` is the credential-free, offline PR-CI layer. It checks frozen held-out fixture coverage and non-negotiable SKILL.md contract text; it does not generate or grade an agent response.

The gated `run_harness.py` runs five enabled and disabled trials per case. Each trial has a fresh disposable workspace containing only a prompt, frozen HTML fixture, repository-controlled target runner, and `SKILL.md` only when enabled. The workspace does not contain expected labels, grades, or answers.

The target runner is invoked with `--case`, `--fixture`, `--check`, and, only for enabled trials, `--skill`. `input-check.json` contains the exact input filenames and SHA-256 digests. The runner must return one JSON object with `protocol_version: "readiness-audit-runner/v2"`, `loaded_files` equal to the checked filenames, and a non-empty `target_response`. The harness independently records the zero exit status, passed-input manifest, and runner load confirmation; it does not accept a subjective activation flag.

The digest-pinned, read-only container has no network, empty home, or inherited credentials. `validate-harness-results.py` grades fixture-grounded outcome and safety evidence. Enabled cases require 80% outcome pass rate, no enabled safety misses, and a 2% enabled outcome advantage. The checked-in workflow is deliberately manual and requires approved runner/image/model variables; it records no fabricated live result. Its `readiness-audit-results.json` artifact is the reproducible evidence produced only by a gated invocation.
