# Ecommerce policy readiness check commands

Replace `$PDP`, `$CART`, `$SHIPPING`, `$RETURNS`, `$TERMS`, and `$SUPPORT` with public storefront URLs. Do not submit forms, start checkout, or place an order.

## Policy availability and readable text

```bash
for url in "$SHIPPING" "$RETURNS" "$TERMS" "$SUPPORT"; do
  printf '%s ' "$url"; curl -sS -L --max-time 20 -o /dev/null -w '%{http_code} %{url_effective}\n' "$url"
done
for url in "$SHIPPING" "$RETURNS"; do
  printf '\n--- %s ---\n' "$url"
  curl -sS -L --max-time 20 "$url" | sed 's/<[^>]*>/ /g' | tr -s ' ' | head -c 2000
  printf '\n'
done
```

Record exact public wording for delivery scope, return window, refund timing, cancellation, and exclusions. Missing or contradictory wording is a policy gap.

## Buyer-surface links and support escalation

```bash
for url in "$PDP" "$CART"; do
  printf '\n--- %s ---\n' "$url"
  curl -sS -L --max-time 20 "$url" | grep -oiE 'href=["'"'][^"'"']*(shipping|delivery|return|refund|cancel)[^"'"']*["'"']' | sort -u
done
curl -sS -L --max-time 20 "$SUPPORT" | grep -oiE 'email|phone|chat|contact|response.{0,40}(hour|day)' | head -30
```

If a policy link is absent, record the surface. Without a published support route, restrict an agent to drafting or collecting information rather than promising resolution.
