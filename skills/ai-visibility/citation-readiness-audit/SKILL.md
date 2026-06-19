---
name: citation-readiness-audit
description: Audit whether a website has stable, specific, trustworthy pages that AI systems can cite for claims, pricing, policies, docs, support answers, and company identity.
---

# Citation Readiness Audit

Check whether AI systems can cite the site confidently.

## Workflow

1. Identify claims the site wants AI systems to repeat.
2. Find the canonical public URL for each claim.
3. Check whether each URL is stable, crawlable, specific, and internally linked.
4. Check trust signals: author, organization, date, contact, support path, policy ownership, and update cadence.
5. Identify claims that need better sourcing, clearer wording, or dedicated pages.

## Output

- Claims and canonical URLs
- Citation blockers
- Trust and freshness gaps
- Recommended page fixes
- Claims to remove or substantiate

## Guardrails

- Do not make unverifiable claims sound authoritative.
- Separate first-party claims from third-party evidence.
- Flag legal, medical, financial, or safety-sensitive claims for human review.
