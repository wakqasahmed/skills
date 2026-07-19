#!/usr/bin/env bash

set -euo pipefail

SUPPORT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "${SUPPORT_ROOT}/../.." && pwd)"
SKILL="$REPO_ROOT/skills/engineering/ai-agent-pr-metadata/SKILL.md"

grep -Fq 'agent:<model+version>-<effort>-<role>' "$SKILL"
grep -Fq 'agent:gpt5.6-terra-medium-implementer' "$SKILL"
grep -Fq 'Never replace the resolved model version or declared effort with an alias or a stronger/weaker value.' "$SKILL"
grep -Fq 'a product alias is not evidence of a model ID' "$SKILL"
grep -Fq 'If the resolved model ID is unavailable, do not create an agent-role label.' "$SKILL"
grep -Fq 'Final OCR Disposition Gate' "$SKILL"
grep -Fq '<!-- ocr-disposition:COMMENT_ID -->' "$SKILL"

echo "ai-agent-pr-metadata tests passed"
