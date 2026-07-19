---
name: commerce-protocol-readiness
description: Audit an ecommerce storefront for agentic commerce protocols and action readiness. Use when checking ACP, UCP, AP2, x402, MPP, MCP, A2A, OAuth, checkout, order, and payment readiness.
---

# Commerce Protocol Readiness

## Workflow

1. Classify the commerce goal: discovery only, assisted checkout, native agent checkout, account linking, order support, paid API/tool access, or machine-to-machine payment.
2. Check public discovery signals: documented API catalog, `.well-known` endpoints, MCP server card, A2A agent card, WebMCP, Agent Skills, link headers, and developer docs.
3. Check checkout readiness: cart creation, pricing/tax/shipping recalculation, inventory reservation, checkout session handoff, order confirmation, returns/refunds, and support escalation.
4. Map protocols to the goal:
   - ACP: agent-initiated checkout where the merchant remains merchant of record.
   - UCP: broader lifecycle coverage across search, cart, identity linking, checkout, order, and post-purchase support.
   - AP2: cryptographic payment authorization and user-consent proof.
   - x402 or MPP: paid API requests, content access, tool calls, or machine-to-machine payments.
   - MCP: exposing merchant tools, catalog lookup, policy lookup, support tools, or order tools to agents.
   - A2A: delegating work between agents using explicit capabilities.
5. Score each protocol as `not applicable`, `missing`, `partial`, `ready`, or `verified`, with evidence.
6. Recommend the smallest next implementation that improves buyer value and merchant control.

## Guardrails

- Do not treat a protocol as required just because it exists. Tie it to a concrete customer or agent workflow.
- Do not recommend autonomous payments without identity verification, consent capture, audit logs, fraud controls, and human escalation.
- See `../references/guardrails.md` for shared cross-skill guardrails (autonomous action safety, evidence provenance, internal runtime disclosure).
