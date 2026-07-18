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

Run the checks with the commands in `references/checks.md` and cite command output as evidence for each finding.

## Delegation

- Access-file depth (robots, sitemap, llms.txt) → `llms-txt-and-crawler-access`.
- Structured-data depth → `schema-markup-audit` from the ai-visibility pack.
- Scoring and routing the whole store → `readiness-audit`; this skill feeds its agent-access dimension.

## Guardrails

- Separate read readiness from action readiness.
- Return explicit blocker codes for unavailable crawl access, raw-HTML product gaps, missing product facts, policy/support gaps, or an unknown action boundary; do not call an action safe merely because catalog content is readable.
- See `../references/guardrails.md` for shared cross-skill guardrails (autonomous action safety, evidence provenance, internal runtime disclosure).
