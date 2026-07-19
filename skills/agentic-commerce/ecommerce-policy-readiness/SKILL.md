---
name: ecommerce-policy-readiness
description: Assess whether ecommerce policies are clear enough for AI answers, support drafts, and supervised order workflows.
---

# Ecommerce Policy Readiness

## Workflow

1. Check shipping, delivery, returns, refunds, warranty, payment, cancellations, substitutions, and support escalation.
2. Identify ambiguity that would cause wrong AI answers or unsafe support drafts.
3. Check whether policies are linked from product, cart, checkout, and support surfaces.
4. Convert policy gaps into answer-ready snippets and escalation rules.

Run the checks in `references/checks.md` and cite the observed output for each finding.

## Output

- Policy gap
- Risk to buyer or operator
- Suggested wording/fix
- Whether a custom agent needs a rule, memory item, or integration

## Guardrails

- Ground every policy answer or draft in a verified, current policy source; never infer a return, refund, delivery, warranty, or cancellation term from a product page or common practice.
- Return `HOLD` with the missing policy fact while it can be collected. Return `BLOCK` when a material policy, exception, or authority cannot be verified.
- Keep refunds, cancellations, substitutions, and order changes supervised by the merchant's authorized workflow; policy readability is not authority to execute an action.
- State the evidence source, the buyer or operator risk, and the escalation path for every unresolved material policy gap.
