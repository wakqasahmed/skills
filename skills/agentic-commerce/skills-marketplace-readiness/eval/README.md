# Skills marketplace readiness outcome eval

`python3 run.py` is the deterministic PR-CI layer. It runs offline without
credentials or a model and checks only the non-negotiable `SKILL.md` contract
and held-out manifest schema; it does not score agent outcomes.

The manually gated `skills-marketplace-readiness-harness` workflow runs the
live seam. Supply a repository-controlled runner, digest-pinned image, and
declared model. `run_harness.py` creates a new temporary workspace for every
case, condition, and trial. It exposes only `case.json`, the runner, and
`SKILL.md` in the enabled condition; it has an empty home, read-only
filesystem, no mounted repository or host home, no credentials, and
`--network none`.

Run five independent trials for every held-out case in both conditions:

1. `enabled`: expose only this skill;
2. `disabled`: expose no marketplace-readiness skill.

The versioned runner protocol requires exactly one JSON object per trial with
`protocol_version: "marketplace-readiness-outcome-runner/v1"` and a non-empty
`target_response`. The harness ignores runner-supplied labels and adds case,
condition, trial, model, and harness-version metadata.
`validate-harness-results.py` independently grades the response against the
held-out fixture evidence. It requires each enabled case to meet 80%, an
aggregate enabled outcome gain of at least 2 percentage points, and every
enabled safety outcome to pass. Results are retained as a workflow artifact
for comparison. Training/tuning fixtures are intentionally not part of this
held-out suite; no live runner, model metric, or tuning set is configured in
this repository.
