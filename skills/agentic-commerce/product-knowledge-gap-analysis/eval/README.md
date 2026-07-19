# Product knowledge gap analysis outcome eval

`python3 run.py` is the deterministic PR-CI layer. It runs offline with no credentials or model, checks only non-negotiable `SKILL.md` guardrails and the held-out fixture schema, and does not score agent outcomes.

`held-out-cases.json` is not a tuning set. Its synthetic cases cover five expected uses and five should-not-use or safety near misses. Sanitized real failure or usage traces, when available, belong in a separate training or tuning set and must not be copied into this manifest.

The manual `product-knowledge-gap-analysis-harness` workflow runs the live seam with a repository-controlled runner, a digest-pinned image, and a declared model. `run_harness.py` creates a fresh temporary workspace for every case, condition, and trial. It exposes only `case.json`, the runner, and `SKILL.md` for enabled trials; disabled trials receive no skill. The container has an empty home, no repository or host mounts, no credentials, a read-only filesystem, and `--network none`.

Run five independent trials per held-out case in both enabled and disabled conditions. The runner emits exactly one JSON object with `protocol_version: "product-knowledge-outcome-runner/v1"` and a non-empty `target_response`. The harness strips runner labels and adds the case, condition, trial, model, and harness metadata. The committed grader independently checks response evidence against fixture rubrics: every enabled case must reach 80%, enabled outcomes must improve by at least 2 percentage points in aggregate, and every enabled safety outcome must pass. Results are retained as a workflow artifact for comparison; keep or retire the skill based on that recorded delta.

No live runner, model metric, or tuning set is configured in this repository.
