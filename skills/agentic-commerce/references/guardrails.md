# Shared guardrails

Canonical wording for guardrails that recur across multiple skills in this pack. Skills reference
this file from their own `## Guardrails` section instead of restating these rules in their own
words. Rules that apply to only one skill stay inline in that skill's `SKILL.md`.

## Autonomous action safety

Do not recommend autonomous checkout, payment, or support actions without approval workflows,
policy grounding, audit logging, and a human escalation path. Autonomous payment execution
additionally requires identity verification, consent capture, and fraud controls before it is
recommended.

## Evidence provenance

Label findings as public-signal evidence unless the user has explicitly provided verified exports
(for example Search Console, analytics, order data, or internal implementation access). Do not
imply access to data, systems, or scores that were not verified this way.

## Internal runtime disclosure

Position any recommended build as a custom agent or public-facing offer. Do not name or expose
internal runtime products, infrastructure, or implementation details publicly.
