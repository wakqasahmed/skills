---
name: fde-opportunity-map
description: Identify when an ecommerce prospect needs Forward Deployed Engineering beyond a standard custom-agent setup.
---

# FDE Opportunity Map

## Workflow

1. Look for custom platform, ERP, PIM, OMS, support, feed, checkout, protocol, or workflow integration needs.
2. Separate configuration work from engineering delivery.
3. Identify dependencies, data contracts, approval gates, and operational risk.
4. Propose a small FDE sprint with clear outcome and verification.

Run the checks in `references/checks.md` against the proposed integration inventory before sizing an FDE sprint.

## Output

- Integration/workflow need
- Why custom-agent setup alone is insufficient
- Required systems and owners
- Smallest useful FDE scope
- Verification and rollback path

## Guardrails

- Recommend FDE only when a verified custom integration or workflow constraint exceeds configuration of the standard custom-agent setup.
- Do not present a discovery finding as an approved integration, data contract, production access, or authorization to change an operational system.
- Define the smallest reversible sprint with named system owners, approval gates, success evidence, and a rollback path before proposing delivery.
