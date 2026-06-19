---
name: llms-txt-generator
description: Draft or review an `llms.txt` file from a site's public pages, docs, sitemap, products, policies, and support content. Use when a user wants AI agents to understand the most important URLs and context.
---

# llms.txt Generator

Create a concise `llms.txt` draft that points AI agents to the most useful public resources.

## Workflow

1. Inspect the homepage, sitemap, docs, product/service pages, policy pages, and support pages.
2. Identify canonical high-value URLs and exclude thin, duplicate, private, or low-signal pages.
3. Group links by intent: overview, products/services, docs, support, policies, changelog, pricing, and contact.
4. Draft `llms.txt` with short descriptions for each section.
5. Note missing pages that would make the file more useful.

## Output

- Proposed `llms.txt`
- Placement path: `/llms.txt`
- Source URLs used
- Missing recommended URLs or pages
- Verification steps

## Guardrails

- Do not fabricate URLs.
- Do not include private, authenticated, admin, staging, or customer-specific pages.
- Keep descriptions factual and brief.
