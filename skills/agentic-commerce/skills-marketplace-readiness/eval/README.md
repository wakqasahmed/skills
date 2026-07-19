# Skills marketplace readiness outcome eval

`python3 run.py` is the deterministic PR-CI layer. It is offline and checks
only the non-negotiable skill contract and held-out fixture shape.

The manually gated workflow runs five independent trials for every fixture in
both conditions. Each disposable container has a read-only root and fixture
mount, an empty home, a writable tmpfs only, and `--network none`. Enabled
trials receive `SKILL.md`; disabled trials do not.

`target_agent_runner.py` is the checked-in target-agent contract. The
digest-pinned image must provide `/opt/marketplace-agent/bin/agent`, a
self-contained agent runtime/model, with these arguments: `--model`,
`--request`, `--repository`, `--output`, and `--trial`; it must write a JSON
action artifact to the requested output path. The runner invokes that command
in both conditions; no repository variable selects executable code.

An artifact has `schema_version: 1`, `safety: "no_external_action"`, a
`verdict`, an `action`, and an `evidence` list of repository-relative file
paths. The runner sees only the
prompt and realistic repository fixture. `expected-outcomes.json` is never
mounted into the target workspace. The validator independently checks that the
artifact's action and cited files match the held-out repository state,
including five out-of-scope/no-use cases. It requires each enabled case to
pass 80%, an aggregate enabled artifact gain of at least two points, and no
safety regression. The container independently prevents network or repository
writes in every trial.
Results are retained as a workflow artifact.
