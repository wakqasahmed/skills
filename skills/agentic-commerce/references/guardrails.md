# Shared guardrails

Canonical wording for guardrails that recur across multiple skills in this pack. Skills reference
this file from their own `## Guardrails` section instead of restating these rules in their own
words. Rules that apply to only one skill stay inline in that skill's `SKILL.md`.

## Safety-relevant skills

The current safety-relevant skills are `agent-readiness`, `commerce-protocol-readiness`,
`custom-agent-remediation-plan`, `ecommerce-policy-readiness`, `fde-opportunity-map`, and
`readiness-audit`. They assess or plan agent-executed checkout, payment, support, order, or other
operational commerce actions and must reference this contract.

## Autonomous action safety

Do not recommend autonomous checkout, payment, support, order, or other operational commerce
actions without approval workflows, policy grounding, audit logging, and a human escalation path.
Autonomous payment execution additionally requires all of the following before it is recommended:
identity verification, consent capture, and fraud controls, together with
audit logging and a human escalation path.

## Evidence provenance

Label findings as public-signal evidence unless the user has explicitly provided verified exports
(for example Search Console, analytics, order data, or internal implementation access). Do not
imply access to data, systems, or scores that were not verified this way.

## Internal runtime disclosure

Position any recommended build as a custom agent or public-facing offer. Do not name or expose
internal runtime products, infrastructure, or implementation details publicly.
