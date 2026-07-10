---
name: readiness-audit
description: Route an ecommerce storefront through an Agentic Commerce readiness audit. Use when assessing whether a store should move to Custom Agent, Verified Audit, Forward Deployed Engineering, or Not Qualified.
---

# Readiness Audit

## Workflow

1. Confirm the submitted URL is a public production storefront.
2. Score each dimension below from public signals only, citing at least one URL or check per score.
3. Label evidence as public-signal only unless verified exports are explicitly provided.
4. Route using the thresholds, then state next steps and limitations.

## Scoring rubric

Score each dimension 0-3.

| Dimension | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| SEO basics | Not indexable, or robots/canonical broken | Indexable but thin metadata, weak internal links | Solid metadata and sitemap, minor gaps | Clean indexing, canonicals, sitemap, crawlable pages |
| AEO/GEO content | No answerable content | Some FAQ or policy text, buried or vague | Clear FAQs, policies, comparisons on stable URLs | Rich answer-shaped content with evidence and dates |
| Product knowledge | No structured data, sparse product copy | Partial attributes, no variants or availability | Product schema with price and availability, variant gaps | Complete attributes, variants, stock, offers in structured data |
| Agent access | Crawlers or AI bots blocked | Accessible but client-side-only rendering | Server-rendered content and sitemap, no agent affordances | Explicit affordances: `llms.txt`, feeds, or API/protocol paths |
| Policy/support | Policies missing or contradictory | Policies vague on returns, shipping, refunds | Clear policies and findable support channels | Policies precise enough for an agent to answer or act on |
| Commerce/action readiness | No bounded actions possible | Checkout works for humans only | Clear cart/checkout flow an agent could supervise | Protocol or API path toward agent-driven ordering |

## Routing thresholds

- Any dimension at 0, or total ≤ 6 → **Not Qualified**. Fix blocking gaps first; hand off to `ai-search-remediation-plan`.
- Total 7-11 → **Verified Audit**. Signals are mixed; verified exports (Search Console, analytics, order data) are needed before recommending a build.
- Total ≥ 12 with agent access ≥ 2 and policy/support ≥ 2 → **Custom Agent**. Hand off to `custom-agent-remediation-plan`.
- Total ≥ 12 but a standard setup cannot cover the platform, protocol, or integration gaps → **Forward Deployed Engineering**. Confirm with `fde-opportunity-map`.

A worked example with scores, evidence, and routing is in `references/example-audit.md`.

## Guardrails

- Do not imply access to Search Console, analytics, revenue, logs, rankings, or conversions unless the user provided verified exports.
- Do not name internal runtime products publicly.
- Prefer practical remediation over generic score commentary.
