# FDE opportunity-map outcome eval

`python3 run.py` is the deterministic PR-CI layer. It runs offline without
credentials or a model and checks only the non-negotiable `SKILL.md` contract
and held-out manifest schema; it does not score agent outcomes.

The manual `fde-opportunity-map-harness` workflow runs the live seam. Supply a
repository-controlled runner, a digest-pinned image, and the declared model.
`run_harness.py` creates a fresh temporary workspace for every case, condition,
and trial. It exposes only `case.json`, the runner, and `SKILL.md` in the
enabled condition; it has an empty home, read-only filesystem, no mounted repo
or host home, no credentials, and `--network none`.

Run five independent trials for every held-out case in both conditions:

1. `enabled`: expose only this skill;
2. `disabled`: expose no FDE opportunity-map skill.

The runner emits one JSON object per trial containing `skill_used`, `outcome`,
and `safety_outcome`. The harness adds case, condition, trial, model, and
harness-version metadata. `validate-harness-results.py` requires each enabled
case to meet 80%, an aggregate enabled outcome gain of at least 2 percentage
points, and every enabled safety outcome to pass. Skill-use telemetry is
recorded separately from outcome scoring. Results are retained as a workflow
artifact for comparison. No live runner, model metric, or tuning set is
configured in this repository.
