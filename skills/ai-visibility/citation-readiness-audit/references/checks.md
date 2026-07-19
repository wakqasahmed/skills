# Citation readiness check commands

Replace `$SITE` with the site origin and `$URL` with the canonical page for a specific claim.

## Confirm the claim's canonical URL is stable and crawlable

```bash
curl -s -o /dev/null -w "%{http_code} %{url_effective}\n" "$URL"
curl -s "$URL" | grep -oiE '<link[^>]+rel="canonical"[^>]*>'
curl -s "$URL" | grep -oiE '<meta[^>]+robots[^>]+>'
```

A 3xx redirect chain, a non-self-referential canonical, or a `noindex` on the page a claim lives on means AI systems are unlikely to treat it as citable — flag as a blocker.

## Verify the claim text actually appears in server-rendered content

```bash
curl -s "$URL" | python3 -c "
import sys, re
html = sys.stdin.read()
text = re.sub('<[^<]+?>', ' ', html)
text = re.sub(r'\s+', ' ', text).strip()
print(text)
" | grep -iF "REPLACE_WITH_EXACT_CLAIM_SUBSTRING"
```

If the grep finds nothing, the claim is either client-rendered only or not actually on that page — do not mark it citable.

## Check trust and freshness signals on the claim's page

```bash
curl -s "$URL" | grep -oE '<script type="application/ld\+json">[^<]*' | sed 's/^<script[^>]*>//' | python3 -m json.tool
curl -s "$URL" | grep -oiE '<meta[^>]+property="article:(published|modified)_time"[^>]*>'
curl -s "$URL" | grep -oiE '(author|by)[^<]{0,40}'
curl -s "$URL" | grep -oiE '(updated|last modified|effective date)[^<]{0,40}'
```

## Check for an identifiable organization/author entity backing the claim

```bash
curl -s "$SITE" | grep -oE '<script type="application/ld\+json">[^<]*' | sed 's/^<script[^>]*>//' | python3 -c "
import json,sys
def find_org(o):
    if isinstance(o,dict):
        if o.get('@type') in ('Organization','Person'): print(json.dumps(o)[:300])
        [find_org(v) for v in o.values()]
    elif isinstance(o,list): [find_org(v) for v in o]
for block in sys.stdin.read().split('\n'):
    try: find_org(json.loads(block))
    except Exception: pass
"
```

## Check for a working contact/support path (baseline trust signal)

```bash
curl -s -o /dev/null -w "%{http_code}\n" "$SITE/contact"
curl -s -o /dev/null -w "%{http_code}\n" "$SITE/support"
```

## Evidence discipline

Record each finding as: claim text, canonical URL, command run, observed output, and whether the claim is stable, current, sourced, and internally linked. A claim without a verifiable canonical URL and matching on-page text must be flagged for sourcing or removal, not marked citable.
