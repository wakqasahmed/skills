# Promotional-offer outcome eval

`bash skills/04-promotional-offer/eval/run-eval.sh` is the deterministic CI layer. It needs only Python's standard library and synthetic held-out fixtures. `contract_check.py` mutation-tests non-negotiable `SKILL.md` rules; `evaluate_outcomes.py` separately scores frozen agent records against the held-out answer key and does not reimplement promotional policy.

The manually dispatched harness runs `run_harness.py` in a fresh temporary workspace for every enabled/disabled condition and trial. `harness-config.json` pins the repository-controlled runner digest, immutable image digest, and required model/harness revisions. Each workspace contains only prompts, the repository-controlled harness runner, and `SKILL.md` in the enabled condition; expected outcomes never enter the container. Docker uses a read-only filesystem, `--network none`, no checkout mount, and a non-existent home directory. The runner must emit its configured metadata and JSON records containing `name`, `condition`, `trial`, and `outcome`.

Use 3--6 trials per case. The gate requires at least an 80% enabled pass rate and a strictly positive enabled-versus-disabled outcome delta. The workflow records the model and harness versions as dispatch inputs and retains the JSON report as an artifact. Keep training or tuning examples out of `fixtures/held-out-scenarios.json`.
