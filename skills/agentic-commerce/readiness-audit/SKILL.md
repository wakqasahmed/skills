---
name: readiness-audit
description: Route an ecommerce storefront through an Agentic Commerce readiness audit. Use when assessing whether a store should move to Custom Agent, Verified Audit, Forward Deployed Engineering, or Not Qualified.
---

# Readiness Audit

## Workflow

1. Confirm the submitted URL is a public production storefront.
2. Score public signals only: SEO basics, AEO/GEO content, product knowledge, agent access, policy/support, commerce/action readiness.
3. Label evidence as public-signal only unless verified exports are explicitly provided.
4. Route to one path: Custom Agent, Verified Audit, Forward Deployed Engineering, or Not Qualified.
5. State next steps and limitations.

## Guardrails

- Do not imply access to Search Console, analytics, revenue, logs, rankings, or conversions unless the user provided verified exports.
- Do not name internal runtime products publicly.
- Prefer practical remediation over generic score commentary.
