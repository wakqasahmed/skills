#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path


DISPOSITION_RE = re.compile(r"<!--\s*ocr-disposition\s*:\s*(\d+)\s*-->", re.IGNORECASE)
FIELD_RE = re.compile(r"^(Disposition|Commit|Test|Issue|Reason):\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
LOCAL_CREDENTIAL_PATH_RE = re.compile(
    r"(?:~|/(?:home|Users)/[^/\s]+)/(?:[^\s]*?/)?(?:\.config/)?[^\s]*(?:credential|credentials|token|secret|hosts\.yml|\.env)[^\s]*",
    re.IGNORECASE,
)
OCR_MARKER_RE = re.compile(r"<!--\s*ocr-", re.IGNORECASE)
BLOCKING_RE = re.compile(r"\bblocking\s*:", re.IGNORECASE)
ROLE_LABEL_RE = re.compile(r"^agent:(.+)-(low|medium|high)-(implementer|reviewer|fixer)$")
AUTHORIZED_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}
RESOLVED_MODEL_RE = re.compile(r"^\s*- Resolved model ID:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
METADATA_LIMITATION_RE = re.compile(r"^\s*- Metadata limitation:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
VERIFIED_AGENT_LABELS_RE = re.compile(r"^\s*- Verified agent labels:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
LEGACY_AGENT_LABELS_RE = re.compile(r"^\s*- Legacy agent labels:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
OCR_GATE_CONTEXT = "OCR disposition gate"


def validate_public_output(output):
    if LOCAL_CREDENTIAL_PATH_RE.search(output):
        return ["Public output contains a local credential-file path"]
    return []


def ocr_findings(head_sha, review_comments):
    return [
        comment
        for comment in review_comments
        if comment.get("commit_id") == head_sha
        and comment.get("user", {}).get("login") == "github-actions[bot]"
        and OCR_MARKER_RE.search(comment.get("body", ""))
    ]


def is_authorized_disposition(comment):
    return comment.get("author_association") in AUTHORIZED_ASSOCIATIONS


def dispositions_by_finding(issue_comments):
    dispositions = {}
    unauthorized = set()
    for comment in issue_comments:
        body = comment.get("body", "")
        marker = DISPOSITION_RE.search(body)
        if not marker:
            continue
        finding_id = int(marker.group(1))
        if not is_authorized_disposition(comment):
            unauthorized.add(finding_id)
            continue
        fields = {key.lower(): value.strip() for key, value in FIELD_RE.findall(body)}
        dispositions[finding_id] = fields
    return dispositions, unauthorized


def disposition_error(finding_id, fields, blocking, pr_commit_shas):
    disposition = fields.get("disposition")
    if disposition not in {"fixed", "deferred", "declined"}:
        return f"OCR finding {finding_id} on latest head is undispositioned"
    if set(fields) - {"disposition", "reason"}:
        return f"OCR finding {finding_id} must use only disposition and reason"
    if blocking and disposition != "fixed":
        return f"Blocking OCR finding {finding_id} must be fixed"
    reason = fields.get("reason", "")
    if not re.fullmatch(r"[^.!?\n]+[.!?]", reason):
        return f"OCR finding {finding_id} needs a one-sentence reason"
    return None


def validate_ocr_dispositions(head_sha, review_comments, issue_comments, pr_commits=()):
    dispositions, unauthorized = dispositions_by_finding(issue_comments)
    pr_commit_shas = {commit["sha"] for commit in pr_commits}
    failures = []
    for finding in ocr_findings(head_sha, review_comments):
        finding_id = finding["id"]
        if finding_id not in dispositions and finding_id in unauthorized:
            failures.append(f"OCR finding {finding_id} has no authorized disposition")
            continue
        failure = disposition_error(
            finding_id,
            dispositions.get(finding_id, {}),
            bool(BLOCKING_RE.search(finding.get("body", ""))),
            pr_commit_shas,
        )
        if failure:
            failures.append(failure)
    return failures


def validate_agent_labels(labels, resolved_model_id=None):
    failures = []
    for label in labels:
        if not label.startswith("agent:"):
            continue
        match = ROLE_LABEL_RE.fullmatch(label)
        if not resolved_model_id or not match or match.group(1) != resolved_model_id:
            failures.append(f"Invalid agent label: {label}")
    return failures


def recorded_labels(match):
    if not match or match.group(1).strip().lower() == "n/a":
        return set()
    return {label.strip() for label in match.group(1).split(",") if label.strip()}


def validate_pr_agent_metadata(pr, legacy_agent_labels=()):
    labels = [label["name"] for label in pr.get("labels", [])]
    body = pr.get("body") or ""
    model_match = RESOLVED_MODEL_RE.search(body)
    limitation_match = METADATA_LIMITATION_RE.search(body)
    verified_labels = recorded_labels(VERIFIED_AGENT_LABELS_RE.search(body))
    legacy_labels = recorded_labels(LEGACY_AGENT_LABELS_RE.search(body))
    actual_agent_labels = {label for label in labels if label.startswith("agent:")}
    trusted_legacy_labels = actual_agent_labels & set(legacy_agent_labels)
    new_agent_labels = actual_agent_labels - trusted_legacy_labels

    if not model_match:
        return ["PR is missing the resolved model ID record"]

    resolved_model_id = model_match.group(1)
    if resolved_model_id.lower() == "unavailable":
        if not limitation_match or limitation_match.group(1).lower() in {"n/a", "unavailable"}:
            return ["PR with unavailable model ID needs a metadata limitation"]
    elif not limitation_match or limitation_match.group(1).lower() != "n/a":
        return ["PR with a resolved model ID must record Metadata limitation: N/A"]

    current_model_id = None if resolved_model_id.lower() == "unavailable" else resolved_model_id
    failures = validate_agent_labels(new_agent_labels, current_model_id)
    for label in sorted(new_agent_labels - verified_labels):
        failures.append(f"Unverified agent label: {label}")
    for label in sorted(verified_labels - new_agent_labels):
        failures.append(f"Verified agent label is not applied: {label}")
    if legacy_labels != trusted_legacy_labels:
        failures.append("Legacy agent labels do not match the base-ref baseline")
    return failures


def validate_required_status_check_policy(rulesets):
    for ruleset in rulesets:
        if ruleset.get("enforcement") != "active":
            continue
        ref_name = ruleset.get("conditions", {}).get("ref_name", {})
        if "~DEFAULT_BRANCH" not in ref_name.get("include", []):
            continue
        for rule in ruleset.get("rules", []):
            if rule.get("type") != "required_status_checks":
                continue
            checks = rule.get("parameters", {}).get("required_status_checks", [])
            if any(check.get("context") == OCR_GATE_CONTEXT for check in checks):
                return []
    return [f"Default branch must require {OCR_GATE_CONTEXT}"]


def read_json(path):
    return json.loads(Path(path).read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--review-comments", required=True)
    parser.add_argument("--issue-comments", required=True)
    parser.add_argument("--pr-commits", required=True)
    parser.add_argument("--pr", required=True)
    parser.add_argument("--legacy-agent-labels", required=True)
    parser.add_argument("--new-agent-label", action="append", default=[])
    parser.add_argument("--resolved-model-id")
    args = parser.parse_args()

    failures = validate_ocr_dispositions(
        args.head_sha,
        read_json(args.review_comments),
        read_json(args.issue_comments),
        read_json(args.pr_commits),
    )
    failures.extend(validate_agent_labels(args.new_agent_label, args.resolved_model_id))
    failures.extend(validate_pr_agent_metadata(
        read_json(args.pr),
        read_json(args.legacy_agent_labels),
    ))
    if failures:
        print("PR governance gate failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("PR governance gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
