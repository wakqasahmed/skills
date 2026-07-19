# Custom-agent remediation plan checks

Set `$PLAN` to a local JSON file containing proposed remediation items. Each item must include `id`, `bucket`, `owner`, `acceptance_test`, and `evidence_source`.

## Validate plan completeness

```bash
jq -e 'type == "array" and length > 0' "$PLAN"
jq -e 'all(.[]; (.id | type == "string" and length > 0) and (.bucket | IN("content"; "product_knowledge"; "crawler_access"; "policy"; "integration"; "workflow")) and (.owner | type == "string" and length > 0) and (.acceptance_test | type == "string" and length > 0) and (.evidence_source | type == "string" and length > 0))' "$PLAN"
```

An item without an accountable owner, evidence source, or observable acceptance test is incomplete.

## Separate storefront work from agent work

```bash
jq -r '.[] | [.id, .bucket, .owner, .acceptance_test] | @tsv' "$PLAN"
jq -e 'all(.[]; has("delivery") and (.delivery | IN("storefront"; "agent"; "shared")))' "$PLAN"
```

Add `delivery` before using the second command. Policy, catalog, and crawler-rule changes need storefront delivery; an agent may not compensate for an unknown source of truth.

## Verify readiness lift

```bash
jq -e 'all(.[]; has("baseline_check") and has("post_change_check"))' "$PLAN"
jq -r '.[] | select(.baseline_check == null or .post_change_check == null) | .id' "$PLAN"
```

Each item needs a reproducible before/after check using source audit output as baseline evidence, not an unverified score claim.
