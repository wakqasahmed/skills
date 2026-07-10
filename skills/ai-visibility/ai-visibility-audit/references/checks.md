# AI visibility check commands

Replace `$SITE` with the site origin and `$URL` with a representative high-value page.

## Discoverability

```bash
curl -s "$SITE/robots.txt"
curl -s "$SITE/robots.txt" | grep -i sitemap
curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" "$URL"
curl -sI "$URL" | grep -i "x-robots-tag"
curl -s "$URL" | grep -oiE '<meta[^>]+robots[^>]+>'
curl -s "$URL" | grep -oiE '<link[^>]+canonical[^>]+>'
```

## AI crawler access (edge blocks don't show in robots.txt)

```bash
for ua in GPTBot ClaudeBot PerplexityBot Google-Extended CCBot; do
  printf "%-16s " "$ua"; curl -s -o /dev/null -w "%{http_code}\n" -A "$ua" "$URL"
done
```

## Machine-readable context

```bash
curl -s "$URL" | grep -oE "<title>[^<]*"
curl -s "$URL" | grep -oiE '<meta name="description"[^>]*>'
curl -s "$URL" | grep -oE '<script type="application/ld\+json">[^<]*' | sed 's/^<script[^>]*>//' | python3 -m json.tool
curl -s -o /dev/null -w "%{http_code}\n" "$SITE/llms.txt"
```

## Server-rendered content test

```bash
curl -s "$URL" | grep -oE "<h1[^>]*>[^<]+"
```

If the main heading and body copy are absent from raw HTML, most AI crawlers see an empty page — mark as a critical blocker.

## Evidence discipline

Record each finding as: URL checked, command run, observed output, why it blocks or helps AI visibility. Findings without observed output are inferences and must be labeled as such.
