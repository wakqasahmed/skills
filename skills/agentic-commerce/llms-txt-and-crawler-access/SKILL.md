---
name: llms-txt-and-crawler-access
description: Review crawler and AI-agent access files for ecommerce sites, including robots.txt, sitemap, llms.txt, and AI bot rules.
---

# LLMs.txt And Crawler Access

## Workflow

1. Check `robots.txt` for blocked product/category/policy paths and AI bot rules.
2. Check sitemap availability, freshness, and product/category coverage.
3. Check whether `llms.txt` exists and points to useful public resources.
4. Check canonical URLs and redirects that may confuse crawlers.
5. Recommend minimal changes that improve agent discoverability without exposing private areas.

## Delegation

This skill is the ecommerce-scoped access review. For depth, delegate to the ai-visibility pack instead of duplicating its work:

- Full robots/meta-robots/header analysis → `robots-ai-crawler-audit`.
- Sitemap coverage, canonicals, and redirect chains → `sitemap-discovery-audit`.
- Drafting a new `llms.txt` → `llms-txt-generator`.

## Guardrails

- Never recommend opening admin, cart, checkout session, account, or private order paths to crawlers.
- Keep access recommendations scoped to public storefront evidence.
