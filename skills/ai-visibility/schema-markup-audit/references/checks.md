# Schema markup extraction and property checklists

## Extract structured data

```bash
curl -s "$URL" | grep -oE '<script type="application/ld\+json">[^<]*' | sed 's/^<script[^>]*>//' | python3 -m json.tool
curl -s "$URL" | grep -oiE 'itemtype="[^"]*"' | sort -u
```

List all `@type` values found:

```bash
curl -s "$URL" | grep -oE '<script type="application/ld\+json">[^<]*' | sed 's/^<script[^>]*>//' | python3 -c "
import json,sys
def types(o):
    if isinstance(o,dict):
        t=o.get('@type');
        if t: print(t)
        [types(v) for v in o.values()]
    elif isinstance(o,list): [types(v) for v in o]
for block in sys.stdin.read().split('\n'):
    try: types(json.loads(block))
    except Exception: pass
"
```

## Property checklists by page type

- **Product**: `name`, `image`, `description`, `sku` or `gtin`, `brand`, `offers.price`, `offers.priceCurrency`, `offers.availability`; variants via `hasVariant` or per-variant offers; `aggregateRating`/`review` only if visible on page.
- **Organization**: `name`, `url`, `logo`, `sameAs` (social/profile links), `contactPoint`; one canonical Organization entity site-wide, not one per page.
- **Article/BlogPosting**: `headline`, `datePublished`, `dateModified`, `author` (Person with `name`, ideally `url`), `publisher`.
- **FAQPage**: each `Question`/`acceptedAnswer` pair must match visible on-page Q&A verbatim.
- **BreadcrumbList**: `itemListElement` positions match the visible trail; URLs absolute and canonical.
- **LocalBusiness**: `name`, `address` (PostalAddress), `geo`, `openingHoursSpecification`, `telephone`; type as specific as truthful (`Restaurant`, not `LocalBusiness`).
- **SoftwareApplication**: `name`, `applicationCategory`, `operatingSystem`, `offers` (including free = price 0).

## Verification

- Rich results eligibility: https://search.google.com/test/rich-results
- Generic validation: https://validator.schema.org
- Cross-check every claimed property against visible page content; flag any schema-only claims as mismatches.
