# Product knowledge gap analysis outcome eval

`python3 run.py` is the deterministic PR-CI layer. It runs offline with no credentials or model, checks only non-negotiable `SKILL.md` guardrails and the held-out fixture schema, and does not score agent outcomes.

`held-out-cases.json` is not a tuning set. Its synthetic cases cover five expected uses and five should-not-use or safety near misses. Sanitized real failure or usage traces, when available, belong in a separate training or tuning set and must not be copied into this manifest.

The held-out cases contain realistic catalog and feed records. The target receives only each case's `id`, `prompt`, `catalog`, and `feed`; it never receives `expected_artifact`, usage labels, or scorer rules. For analysis cases the outcome artifact identifies every observed gap by SKU, field, source of truth, and remediation. For non-use cases it must route without inventing gaps, with a route and non-use reason.

The manual `product-knowledge-gap-analysis-harness` workflow runs the live seam with the checked-in `runner.py`, a digest-pinned image, and a declared model. `runner.py` is the repository-controlled contract: the image must provide `/usr/local/bin/product-knowledge-target`, which accepts `--model <declared-model>`, reads one JSON request from stdin, and emits one JSON artifact to stdout. `run_harness.py` creates a fresh temporary workspace for every case, condition, and trial. It exposes only `case.json`, the runner, and `SKILL.md` for enabled trials; disabled trials receive no skill. The container has an empty home, no repository or host mounts, no credentials, a read-only filesystem, and `--network none`.

Run five independent trials per held-out case in both enabled and disabled conditions. The runner emits exactly one JSON object with `protocol_version: "product-knowledge-outcome-runner/v2"` and an artifact object. The harness adds the case, condition, trial, model, and harness metadata. The committed grader compares the artifact with the independent expected result: every enabled case must reach 80% and enabled artifacts must improve by at least 2 percentage points in aggregate. Results are retained as a workflow artifact for comparison; keep or retire the skill based on that recorded delta.

No live image, model metric, or tuning set is configured in this repository.
