---
name: robots-ai-crawler-audit
description: Review robots.txt, meta robots, headers, and AI crawler rules for search and AI-agent access. Use when a user asks why AI tools cannot find, read, or cite their site.
---

# Robots AI Crawler Audit

Check whether crawler access rules help or block AI visibility.

Scope: access rules only. Sitemap coverage belongs to `sitemap-discovery-audit`; drafting `llms.txt` belongs to `llms-txt-generator`; whole-site triage belongs to `ai-visibility-audit`.

## Workflow

1. Fetch `/robots.txt`.
2. Identify global disallow rules, sitemap declarations, crawl delays, and user-agent specific rules.
3. Check page-level `noindex`, `nofollow`, canonical tags, and `X-Robots-Tag` headers on key URLs.
4. Look for AI crawler-specific rules for major bots where visible.
5. Compare access rules against the user's visibility goals.
6. Recommend exact changes only when the desired access policy is clear.

## Output

- Current crawler policy summary
- Blocked high-value paths
- AI crawler implications
- Recommended robots.txt changes
- Verification commands

## Guardrails

See [Shared Guardrails](../references/guardrails.md) for the cross-cutting rules on not
exposing private/sensitive paths and not claiming AI platform outcome guarantees.

- Call out tradeoffs between visibility, cost, scraping risk, and content control.
