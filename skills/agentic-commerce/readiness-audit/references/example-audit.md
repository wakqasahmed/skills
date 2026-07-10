# Worked example — mid-size Shopify apparel store

Submitted URL: `https://example-apparel.com` (public production storefront, confirmed via homepage + a live product page returning 200).

## Scores

| Dimension | Score | Evidence |
|---|---|---|
| SEO basics | 3 | `robots.txt` allows product/category paths, sitemap index at `/sitemap.xml` with fresh lastmod, canonicals self-referencing on sampled PDPs |
| AEO/GEO content | 1 | Shipping/returns exist but are one paragraph each; no FAQ, no comparison or sizing guidance; policy pages lack dates |
| Product knowledge | 2 | `Product` JSON-LD with `offers.price` and `availability` on PDPs; variants (size/color) only in client-side state, absent from schema |
| Agent access | 2 | Server-rendered PDPs, sitemap present; no `llms.txt`, no feed, no API surface |
| Policy/support | 1 | Returns policy silent on international orders and refund timelines; support is a contact form with no stated SLA |
| Commerce/action readiness | 1 | Standard human checkout; no cart permalink or programmatic path |

**Total: 10** — no dimension at 0.

## Routing

Total 10 falls in 7-11 → **Verified Audit**. Public signals show a crawlable store with weak answer content and vague policies; whether a custom agent is worth building depends on demand and support volume, which requires verified exports (Search Console queries, support ticket themes, order data).

## Next steps stated to the user

1. Provide Search Console export and 30 days of support ticket categories for the verified audit.
2. Quick wins regardless of route: expand returns/shipping policy specifics, add variant data to Product schema, publish an FAQ from real ticket themes.
3. Limitation: all scores above are public-signal only; no analytics, rankings, or revenue data were observed.
