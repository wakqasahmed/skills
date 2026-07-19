---
name: custom-agent-remediation-plan
description: Convert Agentic Commerce audit findings into a custom-agent implementation checklist. Use after readiness, SEO/AEO/GEO, product knowledge, or policy gaps are known.
---

# Custom Agent Remediation Plan

## Workflow

Use only after verified audit findings identify remediation gaps.

1. Group findings into content, product knowledge, crawler access, policy, integration, and workflow buckets.
2. Decide what the custom agent can improve directly versus what needs storefront/platform changes.
3. Define required sources of truth: catalog, policies, support inbox, order system, CMS, analytics exports when provided.
4. Produce a setup checklist with acceptance tests.
5. Define how score lift or readiness improvement will be verified.

Run the checks in `references/checks.md` against the audit findings and proposed plan before presenting it.

Classify every remediation item as agent, storefront, or shared delivery. Name an accountable owner, source of truth, observable acceptance test, baseline check, and post-change check for every remediation item.

## Guardrails

- See `../references/guardrails.md` for shared cross-skill guardrails (autonomous action safety, evidence provenance, internal runtime disclosure).
- Do not promise full automation where supervised workflows are safer.
- Do not use a remediation plan as authority to execute customer, order, payment, credential, or production changes.
