# Welcome-onboarding outcome eval

`bash skills/02-welcome-onboarding/eval/run-eval.sh` is the deterministic CI layer. It runs static SKILL.md mutation checks separately from frozen, synthetic outcome scoring. The prompts and evaluator keys are distinct fixture fields; the scorer compares observable decision, reason code, and required outcome elements without reimplementing the skill policy.

The 12 cases are held out from tuning. They cover five valid onboarding outcomes and seven safety or near-miss outcomes, including missing permission, suppression, unverified proof, incomplete QA, transactional relabelling, an undeliverable signup promise, and activation exit.

## Gated clean harness

The manually dispatched workflow runs `run_harness.py` in a fresh temporary workspace for every skill-enabled/disabled condition and trial. It copies only a blinded `name`/`prompt` view of the held-out fixture (no expected or candidate outcome fields), the repository-controlled runner, and `SKILL.md` in the enabled condition. The disposable Docker container has a read-only filesystem, no network, no checkout mount, and a synthetic `HOME`; no credentials, prior artifacts, or the current enabled/disabled condition are supplied to the runner.

Set repository variables `EMAIL_WELCOME_HARNESS` to a tracked executable path, `EMAIL_WELCOME_HARNESS_VERSION` to its immutable version, and `EMAIL_WELCOME_HARNESS_IMAGE` to its approved digest-pinned image (`registry/image@sha256:<64 hex>`). The runner emits JSON records containing `name` and `outcome`; `run_harness.py` stamps the trusted `condition` and `trial` onto each record itself rather than trusting the runner's self-report. It runs 3--6 trials per case, requires an enabled pass rate of at least 80% and a strictly positive enabled-versus-disabled delta, rejects incomplete or duplicate records, and retains a versioned report artifact. It never runs in pull-request CI.
