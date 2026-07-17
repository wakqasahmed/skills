---
name: ai-visibility-audit
description: Audit whether ChatGPT, Claude, Perplexity, Gemini, Google AI Overviews, and other AI agents can discover, understand, cite, and recommend a website. Use when a user asks if their site is visible or ready for AI search.
---

# AI Visibility Audit

Assess a public website for AI-mediated discovery, parsing, citation, and recommendation.

## Workflow

1. Identify the site type: SaaS, ecommerce, marketplace, docs, blog, local business, portfolio, or other.
2. Check discoverability: robots.txt, sitemap, canonical URLs, status codes, noindex, redirects, and blocked assets.
3. Check machine-readable context: title, meta description, headings, internal links, schema markup, feeds, and `llms.txt`.
4. Check answer quality: product/service pages, pricing, policies, FAQs, docs, support pages, and comparison pages.
5. Check citation readiness: dated claims, sources, author/org identity, contact, support, and stable URLs.
6. Rank blockers by impact: critical, important, optional.
7. Produce a prioritized remediation plan.

Run the discoverability and machine-readable checks with the commands in `references/checks.md` and cite command output as evidence.

## Delegation

This is the orchestrator: it finds and ranks blockers, then hands deep dives to the focused skills instead of redoing them inline:

- Robots/meta-robots/header rules → `robots-ai-crawler-audit`
- Sitemap coverage, canonicals, redirects → `sitemap-discovery-audit`
- Structured data depth → `schema-markup-audit`
- Drafting `llms.txt` → `llms-txt-generator`
- Content gaps → `answer-engine-content-audit`; citation trust → `citation-readiness-audit`
- Turning findings into tickets → `ai-search-remediation-plan`

## Output

- Overall score: ready, partially ready, or blocked
- Top 5 blockers
- Evidence with URLs
- Quick wins
- Implementation tickets or next actions

## Guardrails

See [Shared Guardrails](../references/guardrails.md) for the cross-cutting rule on not
claiming AI platform outcome guarantees.

- Distinguish observed page evidence from inferred recommendations.
- Prefer public crawlable evidence unless the user provides private analytics or Search Console data.
