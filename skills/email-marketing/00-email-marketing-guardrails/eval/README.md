# Email guardrails outcome eval

`bash skills/email-marketing/00-email-marketing-guardrails/eval/run-eval.sh` is the deterministic CI layer. It is offline, uses synthetic held-out scenarios, and separates static SKILL.md mutation checks from outcome validation. The outcome validator compares observable decision, reason code, and required next actions from frozen candidate outputs; it deliberately does not reimplement the prose policy.

## Gated harness seam

The manually dispatched harness runs `run_harness.py` in a new temporary workspace per condition/trial, copies only the fixture and (when enabled) `SKILL.md`, clears credentials, invokes the configured repository-controlled runner without a shell, and requires Linux network-namespace isolation. Set the repository variable `EMAIL_GUARDRAILS_HARNESS` to a tracked executable path. The runner must emit JSON records with `name`, `condition`, `trial`, and `outcome`. It runs 3--6 trials per case, requires an enabled pass rate of at least 80% and a positive enabled-versus-disabled delta, rejects duplicate trial records, and retains its JSON report as a workflow artifact. Do not run that harness in pull-request CI.
