# Product knowledge check commands

Replace `$PDP` with a representative product page URL. Repeat for each important product type and variant family.

## Raw product-page evidence

```bash
curl -sS -L --max-time 20 "$PDP" | grep -oE '<h1[^>]*>[^<]+|[[:alnum:]][^<]{0,80}(SKU|GTIN|size|ingredient|material|compatib|allergen|warranty)[^<]{0,120}' | head -80
curl -sS -L --max-time 20 "$PDP" | grep -oiE '(add to cart|out of stock|in stock|sold out|select (a )?(size|color|variant))' | sort -u
```

Record attributes visible in raw HTML. If core facts appear only after client-side interaction, mark them unavailable to basic crawlers.

## Structured product fields and variants

```bash
curl -sS -L --max-time 20 "$PDP" | grep -oE '<script type="application/ld\+json">[^<]*' | sed 's/^<script[^>]*>//' | python3 -m json.tool
curl -sS -L --max-time 20 "$PDP" | grep -oiE 'hasVariant|offers|priceCurrency|availability|sku|gtin' | sort -u
```

Check for a product identifier, price, currency, availability, and variant representation. Treat fields not supported by a visible source as unknown; never infer ingredients, compatibility, or safety claims.

## Catalog-feed comparison when supplied

```bash
curl -sS -L --max-time 20 -o /dev/null -w '%{http_code} %{content_type}\n' "$FEED_URL"
curl -sS -L --max-time 20 "$FEED_URL" | head -c 1000
```

Set `$FEED_URL` only to a public operator-supplied feed. Compare its identifiers and attributes with the product page; mismatches are source-of-truth gaps.
