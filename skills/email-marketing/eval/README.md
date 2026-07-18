# Email marketing behavior eval

Run `bash skills/email-marketing/eval/run-eval.sh`. It uses only synthetic fixtures and the Python standard library.

## Coverage inventory

Existing behavior evals cover `commerce-protocol-readiness`, `readiness-audit`, `ai-visibility-audit`, `clarify-work`, `subagent-pipeline`, and `to-prd`. The aggregate runner invokes every no-network eval, including `commerce-protocol-readiness`; `readiness-audit` needs an API key. This eval closes the highest-risk uncovered decision paths:

- `00-email-marketing-guardrails`: permission, suppression, authentication, identity, claim, and QA outcomes.
- `18-jurisdiction-compliance-routing`: unknown jurisdictions can only `HOLD` while a routing fact is collectable; unverified legal basis is `BLOCK`.
- `19-lifecycle-orchestration`: promotional messages cannot use a service label to bypass marketing rules; suppression, precedence, and caps remain deterministic.

The fixtures require the candidate output to name the exact decision and, where applicable, its reason code. That feedback is reflected in the mandatory decision-output rules of the three skills.
