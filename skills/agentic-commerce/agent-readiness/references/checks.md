# Agent readiness check commands

Replace `$SITE` with the storefront origin and `$PDP` with a representative product page URL.

## 1. Crawl access and URL quality

```bash
curl -s "$SITE/robots.txt"
curl -sI "$PDP" | grep -iE "^(HTTP|x-robots-tag|location|content-type)"
curl -sI -A "GPTBot" "$PDP" | head -1
curl -sI -A "ClaudeBot" "$PDP" | head -1
curl -sI -A "PerplexityBot" "$PDP" | head -1
```

A 403/429 for bot user-agents but 200 for default means AI crawlers are blocked at the edge (CDN/WAF), not in robots.txt.

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
curl -s -o /dev/null -w "%{http_code}\n" "$SITE/.well-known/ai-plugin.json"
curl -s "$SITE/robots.txt" | grep -i sitemap
```

Also note any public product feed (Google Merchant, RSS/Atom) or documented API — each one is an affordance worth citing.
