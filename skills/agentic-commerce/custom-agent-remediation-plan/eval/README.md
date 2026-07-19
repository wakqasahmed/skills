# Custom-agent remediation-plan outcome eval

`python3 run.py` is the deterministic PR-CI layer. It is offline and checks
only the non-negotiable `SKILL.md` contract and held-out manifest schema; it
does not score a live agent outcome.

The manually gated `custom-agent-remediation-plan-harness` workflow runs the
live seam. Supply a repository-controlled runner, digest-pinned image, and
declared model through repository variables. For each held-out case, enabled or
disabled condition, and five independent trials, `run_harness.py` creates a
fresh temporary workspace. It exposes only `case.json`, the runner, and
`SKILL.md` for enabled trials. The container has a read-only filesystem, empty
home, no mounted repository or host home, no credentials, and `--network none`.

The runner must emit one JSON object using
`custom-agent-remediation-outcome-runner/v2` with a non-empty JSON target
response and a `skill_used` boolean. The harness records that activation signal
with the response and case, condition, trial, model, and harness-version
metadata. `validate-harness-results.py` validates remediation artifacts against
the fixture's finding IDs, buckets, and evidence sources; every plan item needs
an owner plus baseline, acceptance, and post-change checks. It validates routes
and non-execution for near misses, and verifies that `skill_used` is true only
for enabled should-use cases. It requires every enabled case to reach 80%, every
enabled safety result to pass, and an aggregate enabled outcome gain of at least
2 percentage points over disabled. Workflow results are retained as an artifact
for comparison.

Fixtures are held out from tuning. This initial set is synthetic; add sanitized
real failure or usage traces as they become available, keeping them held out or
placing tuning-only traces in a separate manifest. No live runner, model metric,
or tuning set is configured in this repository.
