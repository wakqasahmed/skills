# FDE opportunity check commands

Set `$INVENTORY` to a local JSON file listing systems needed for the proposed workflow. Each item must include `system`, `owner`, `data_contract`, `approval_gate`, `verification`, and `rollback`.

## Validate integration inventory

```bash
jq -e 'type == "array" and length > 0' "$INVENTORY"
jq -e 'all(.[]; (.system | type == "string" and length > 0) and (.owner | type == "string" and length > 0) and (.data_contract | type == "string" and length > 0) and (.approval_gate | type == "string" and length > 0) and (.verification | type == "string" and length > 0) and (.rollback | type == "string" and length > 0))' "$INVENTORY"
```

Missing ownership, contract, approval, verification, or rollback means the work is not ready to size as an FDE sprint.

## Distinguish configuration from engineering

```bash
jq -e 'all(.[]; has("delivery") and (.delivery | IN("configuration"; "engineering"; "shared")))' "$INVENTORY"
jq -r '.[] | [.system, .delivery, .owner, .approval_gate] | @tsv' "$INVENTORY"
```

Add `delivery` before using these commands. Systems requiring a new data contract, custom authentication flow, or transactional side effect are engineering candidates; record evidence rather than assuming FDE is needed.

## Confirm bounded verification

```bash
jq -e 'all(.[]; (.verification | test("test|sandbox|staging|fixture"; "i")) and (.rollback | test("disable|revert|rollback|remove"; "i")))' "$INVENTORY"
```

Verification must use a non-production seam. If none exists, stop at discovery and request the missing operational owner or environment.
