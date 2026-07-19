# Answer engine content check commands

Replace `$SITE` with the site origin and `$URL` with a page under review. Most checks here are content inspection, not pure network calls — use curl to pull the raw page, then grep/read for substance.

## Pull server-rendered content (what AI crawlers actually see)

```bash
curl -s "$URL" | grep -oE "<h1[^>]*>[^<]+"
curl -s "$URL" | grep -oE "<h2[^>]*>[^<]+"
curl -s "$URL" | python3 -c "
import sys, re
html = sys.stdin.read()
text = re.sub('<[^<]+?>', ' ', html)
text = re.sub(r'\s+', ' ', text).strip()
print(text[:2000])
"
```

If the heading/body text is missing from raw HTML while the page renders fine in a browser, the content is client-side-only and most AI crawlers will not see it — flag as a critical gap before scoring content quality.

## Inventory candidate answer pages

```bash
curl -s "$SITE/sitemap.xml" | grep -oE '<loc>[^<]+</loc>' | sed -e 's/<loc>//' -e 's/<\/loc>//' \
  | grep -iE 'faq|pricing|compare|vs|docs|support|guide|how-to'
```

## Check for direct-answer patterns on a candidate page

```bash
curl -s "$URL" | grep -ciE '<h[1-6][^>]*>\s*(what|how|why|when|is|can|does)\b'
curl -s "$URL" | grep -oiE '<h[1-6][^>]*>\s*(what|how|why|when|is|can|does)[^<]*'
```

Pages that phrase headings as direct questions are easier for answer engines to extract and cite verbatim.

## Check pricing/comparison clarity (common AI-answer trigger)

```bash
curl -s "$URL" | grep -oiE '\$[0-9,]+(\.[0-9]{2})?'
curl -s "$URL" | grep -ciE '\b(vs\.?|versus|compared to|alternative)\b'
```

Absence of any dollar figure or comparison language on a pricing/comparison-intent page is itself a finding worth recording.

## Freshness signal check

```bash
curl -s "$URL" | grep -oiE '<meta[^>]+property="article:(published|modified)_time"[^>]*>'
curl -s "$URL" | grep -oiE '(updated|last modified|published)[^<]{0,40}'
```

## Evidence discipline

Record each finding as: URL checked, question it was meant to answer, command run, observed excerpt, and whether the answer is present, vague, missing, or unciteable. Do not claim a content gap without pulling the actual rendered text first.
