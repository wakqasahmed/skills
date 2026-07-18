# Email guardrails outcome eval

`bash skills/email-marketing/00-email-marketing-guardrails/eval/run-eval.sh` is the deterministic CI layer. It is offline, uses synthetic held-out scenarios, and separates static SKILL.md mutation checks from outcome validation. The outcome validator compares observable decision, reason code, and required next actions from frozen candidate outputs; it deliberately does not reimplement the prose policy.

## Gated harness seam

No live agent harness is bundled. A scheduled or manually dispatched harness must run each fixture in a clean disposable workspace with network and credentials disabled, once with this skill present and once absent. It must emit one JSON outcome per trial with `name`, `condition`, `decision`, `reason_code`, and `required_actions`; run 3--6 trials per case and retain the report. Gate promotion on at least an 80% pass rate and a positive skill-enabled versus disabled outcome delta. Do not run that harness in pull-request CI.
