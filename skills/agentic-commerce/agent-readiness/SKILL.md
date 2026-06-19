---
name: agent-readiness
description: Check whether AI agents can discover, read, cite, and safely act on an ecommerce storefront. Use for agentic commerce readiness reviews.
---

# Agent Readiness

## Workflow

1. Confirm crawl access and public URL quality.
2. Check product/category/policy readability without client-side-only traps.
3. Check structured product data, variants, availability, price, and policy context.
4. Check whether support and checkout actions are clearly bounded.
5. Identify missing agent-facing affordances such as sitemap, `llms.txt`, markdown-friendly content, or API/protocol paths.

## Guardrails

- Separate read readiness from action readiness.
- Do not recommend autonomous checkout or support actions without approval, policy, and audit controls.
