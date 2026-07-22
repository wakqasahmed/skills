# Lead-nurture outcome eval

`bash skills/03-lead-nurture-education/eval/run-eval.sh` is the deterministic, no-network CI layer. `contract_check.py` checks non-negotiable `SKILL.md` text. `evaluate_outcomes.py` separately scores frozen candidate outcomes against a held-out scoring key; prompts contain neither expected decisions nor required actions.

The gated harness runs `run_harness.py` in a fresh temporary workspace for every case, condition, and trial. It copies only the held-out prompts, repository-controlled runner, and `SKILL.md` for the `enabled` condition. Docker uses `--network none`, a read-only root filesystem, a tmpfs `/tmp`, and a read-only workspace mount. It never mounts the checkout, credentials, or prior conversation artifacts.

The runner must emit a JSON list of records containing `name`, `condition` (`enabled` or `disabled`), `trial`, and `outcome` with `decision` and `actions`. The harness accepts only 3--6 trials and a digest-pinned image. It requires an enabled pass rate of at least 80% and a strictly positive enabled versus disabled delta. The report records the fixture schema, model, harness version, image digest, trial count, threshold, per-condition rates, and all records.

The harness workflow is intentionally scheduled or manually dispatched only. Configure the tracked runner path, digest-pinned image, model identifier, and harness version as repository variables; it is skipped until all are present.
