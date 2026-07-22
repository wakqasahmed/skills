# Agent readiness check commands

Replace `$SITE` with the storefront origin and `$PDP` with a representative product page URL.

## 1. Crawl access and URL quality

```bash
curl -s "$SITE/robots.txt"
curl -sI "$PDP" | grep -iE "^(HTTP|x-robots-tag|location|content-type)"
curl -sI -A "OAI-SearchBot" "$PDP" | head -1
curl -sI -A "Claude-SearchBot" "$PDP" | head -1
curl -sI -A "PerplexityBot" "$PDP" | head -1
```

Use crawler identities according to the audit goal: OAI-SearchBot, Claude-SearchBot, and PerplexityBot for search visibility; GPTBot and ClaudeBot for model-training controls. [SRC-OPENAI-CRAWLERS] [SRC-ANTHROPIC-CRAWLERS] [SRC-PERPLEXITY-CRAWLERS]

Do not send `Google-Extended` as an HTTP user-agent. It is only a robots.txt control token and does not affect Google Search inclusion. [SRC-GOOGLE-EXTENDED]

A 403/429 for search crawler user-agents but 200 for default is evidence of an edge (CDN/WAF) difference. Review robots.txt separately before deciding where the block originates.

## 2. Client-side-only rendering traps

```bash
curl -s "$PDP" | grep -ci "add to cart"
curl -s "$PDP" | grep -oE "<h1[^>]*>[^<]+" | head -3
```

If the product name, price, and description do not appear in the raw HTML, the page is a client-side-only trap for most agents.

## 3. Structured product data

```bash
curl -s "$PDP" | grep -oE '<script type="application/ld\+json">[^<]*' | sed 's/^<script[^>]*>//' | python3 -m json.tool
```

Check for `@type: Product`, `offers.price`, `offers.availability`, and variant coverage (`hasVariant` or per-variant offers). Missing availability or variants blocks agent recommendations.

## 4. Bounded actions

Manual review: from the policy and support pages, can an agent determine what it may do (answer questions, draft returns, place a supervised order) and what it must not? Look for return windows, refund timelines, shipping scope, cancellation rules, and a support channel with stated response expectations.

## 5. Agent-facing affordances

```bash
curl -s -o /dev/null -w "%{http_code}\n" "$SITE/llms.txt"
curl -s -o /dev/null -w "%{http_code}\n" "$SITE/sitemap.xml"
curl -s -o /dev/null -w "%{http_code}\n" "$SITE/.well-known/ucp"
curl -s -o /dev/null -w "%{http_code}\n" "$SITE/.well-known/agent-card.json"
curl -s "$SITE/robots.txt" | grep -i sitemap
```

Probe `/.well-known/ucp` only when UCP is relevant and `/.well-known/agent-card.json` only when the site claims to host an A2A server. Their specifications define those discovery locations. [SRC-UCP] [SRC-A2A]

For a protected remote MCP endpoint, inspect its `401` `WWW-Authenticate` challenge and the referenced OAuth Protected Resource Metadata rather than guessing a site-root manifest. [SRC-MCP]

WebMCP is discoverable inside a supporting browser through `document.modelContext`, not by probing a `.well-known` URL. [SRC-WEBMCP]

The retired `/.well-known/ai-plugin.json` manifest is not a current Agentic Commerce discovery check. For ACP, inspect the merchant's published product feed and versioned API or schema artifacts; for x402 or MPP, inspect a claimed paid endpoint's HTTP 402 challenge. [SRC-ACP] [SRC-X402] [SRC-MPP]

Also note any public product feed (Google Merchant, RSS/Atom) or documented API as observed evidence.
