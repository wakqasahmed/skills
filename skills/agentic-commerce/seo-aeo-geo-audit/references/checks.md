# SEO, AEO, and GEO check commands

Replace `$SITE` with the storefront origin, `$URL` with an indexable page, and `$SITEMAP` with its sitemap URL.

## Indexability and canonical URL

```bash
curl -sS -L --max-time 20 -o /dev/null -w "%{http_code} %{url_effective}\n" "$URL"
curl -sSI -L --max-time 20 "$URL" | grep -iE '^(HTTP|x-robots-tag|location|content-type)'
curl -sS -L --max-time 20 "$URL" | grep -oiE '<meta[^>]+name=["'"']robots["'"'][^>]*>|<link[^>]+rel=["'"']canonical["'"'][^>]*>'
```

Record the final URL, status, robots directives, and canonical. A non-200 final response, `noindex`, or an off-canonical URL is an indexability finding.

## Sitemap and internal discovery

```bash
curl -sS --max-time 20 "$SITEMAP" | grep -F "$URL"
curl -sS -L --max-time 20 "$SITE" | grep -F "$URL"
```

If a canonical page is absent from both sitemap and relevant navigational HTML, record a discovery gap.

## Answer-ready content and crawler access

```bash
curl -sS -L --max-time 20 "$URL" | grep -oE '<title>[^<]*|<h1[^>]*>[^<]+' | head -5
curl -sS -L --max-time 20 "$URL" | grep -oiE '<meta[^>]+name=["'"']description["'"'][^>]*>'
for ua in OAI-SearchBot Claude-SearchBot PerplexityBot; do
  printf '%-16s ' "$ua"; curl -sS -L --max-time 20 -o /dev/null -w '%{http_code}\n' -A "$ua" "$URL"
done
```

These are search crawler identities documented by their publishers. GPTBot and ClaudeBot control model-training crawling instead. [SRC-OPENAI-CRAWLERS] [SRC-ANTHROPIC-CRAWLERS] [SRC-PERPLEXITY-CRAWLERS]

Do not send `Google-Extended` as an HTTP user-agent; it is a robots.txt control token and does not affect Google Search. [SRC-GOOGLE-EXTENDED]

Compare crawler responses with the default response. Different blocked responses are an access finding; check all claims against visible page text.
