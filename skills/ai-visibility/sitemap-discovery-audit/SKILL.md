---
name: sitemap-discovery-audit
description: Audit sitemap coverage, canonical URLs, indexable pages, redirects, and crawl discovery paths. Use when a user wants AI search systems and crawlers to find the right pages.
---

# Sitemap Discovery Audit

Check whether crawlers can discover the site's important public URLs.

Scope: discovery paths only. Access rules (robots, headers, bot blocks) belong to `robots-ai-crawler-audit`; whole-site triage belongs to `ai-visibility-audit`.

## Workflow

1. Find sitemap declarations in robots.txt and common sitemap paths.
2. Inspect sitemap indexes, URL sets, lastmod values, and obvious stale entries.
3. Compare sitemap URLs with navigation, important landing pages, docs, products, policies, and support pages.
4. Check representative URLs for status codes, redirects, canonical tags, and noindex.
5. Identify missing, duplicate, blocked, broken, or low-value sitemap entries.

## Output

- Sitemap paths found
- Coverage gaps
- Broken or blocked URLs
- Canonical and redirect issues
- Priority fixes

## Guardrails

- Do not treat sitemap presence as proof of indexing.
- Prioritize high-value public pages over exhaustive URL counts.
- Flag generated or faceted URLs that may create crawl noise.
