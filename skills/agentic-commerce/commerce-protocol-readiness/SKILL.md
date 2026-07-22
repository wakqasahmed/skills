---
name: commerce-protocol-readiness
description: Audit an ecommerce storefront for agentic commerce protocols and action readiness. Use when checking ACP, UCP, AP2, x402, MPP, MCP, A2A, OAuth, checkout, order, and payment readiness.
---

# Commerce Protocol Readiness

## Workflow

1. Classify the commerce goal: discovery only, assisted checkout, native agent checkout, account linking, order support, paid API/tool access, or machine-to-machine payment.
2. Check only discovery signals defined by the protocol in scope: documented API catalogs, UCP business profiles, A2A Agent Cards, MCP authorization metadata, WebMCP tools in a supporting browser, Agent Skills, link headers, and developer docs. [SRC-UCP] [SRC-A2A] [SRC-MCP] [SRC-WEBMCP]
3. Check checkout readiness: cart creation, pricing/tax/shipping recalculation, inventory reservation, checkout session handoff, order confirmation, returns/refunds, and support escalation.
4. Map protocols to the goal:
   - ACP: agent-assisted discovery and checkout using the merchant's published feed and API artifacts. [SRC-ACP]
   - UCP: commerce lifecycle capabilities negotiated from the business profile at `/.well-known/ucp`. [SRC-UCP]
   - AP2: signed checkout and payment mandates that prove authorization for agent-performed payments. [SRC-AP2]
   - x402: HTTP 402 payment challenges for paid APIs or content. [SRC-X402]
   - MPP: HTTP machine payments for API requests, tool calls, or content. [SRC-MPP]
   - MCP: exposing merchant tools, catalog lookup, policy lookup, support tools, or order tools to agents; protected HTTP servers advertise authorization through OAuth metadata. [SRC-MCP]
   - A2A: delegating work to agents whose capabilities and interfaces are described by an Agent Card. [SRC-A2A]
   - WebMCP: exposing page tools through the draft browser `document.modelContext` API, not through a site-wide manifest. [SRC-WEBMCP]
   - Trusted Agent Protocol: verifying agent identity and commerce intent from signed HTTP requests; it is not a crawler allowlist by itself. [SRC-TAP]
5. Score each protocol as `not applicable`, `missing`, `partial`, `ready`, or `verified`, with evidence.
6. Recommend the smallest next implementation that improves buyer value and merchant control.

## Guardrails

- Do not treat a protocol as required just because it exists. Tie it to a concrete customer or agent workflow.
- Do not recommend autonomous payments without identity verification, consent capture, audit logs, fraud controls, and human escalation.
- See `../references/guardrails.md` for shared cross-skill guardrails (autonomous action safety, evidence provenance, internal runtime disclosure).
