#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path


DISPOSITION_RE = re.compile(r"<!--\s*ocr-disposition\s*:\s*(\d+)\s*-->", re.IGNORECASE)
FIELD_RE = re.compile(r"^(Disposition|Commit|Test|Issue|Reason):\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
OCR_MARKER_RE = re.compile(r"<!--\s*ocr-", re.IGNORECASE)
BLOCKING_RE = re.compile(r"\bblocking\s*:", re.IGNORECASE)
ROLE_LABEL_RE = re.compile(r"^agent:(.+)-(low|medium|high)-(implementer|reviewer|fixer)$")


def ocr_findings(head_sha, review_comments):
    return [
        comment
        for comment in review_comments
        if comment.get("commit_id") == head_sha
        and comment.get("user", {}).get("login") == "github-actions[bot]"
        and OCR_MARKER_RE.search(comment.get("body", ""))
    ]


def dispositions_by_finding(issue_comments):
    dispositions = {}
    for comment in issue_comments:
        body = comment.get("body", "")
        marker = DISPOSITION_RE.search(body)
        if not marker:
            continue
        fields = {key.lower(): value.strip() for key, value in FIELD_RE.findall(body)}
        dispositions[int(marker.group(1))] = fields
    return dispositions


def disposition_error(finding_id, fields, blocking):
    disposition = fields.get("disposition")
    if disposition not in {"fixed", "deferred", "declined"}:
        return f"OCR finding {finding_id} on latest head is undispositioned"
    if blocking and disposition != "fixed":
        return f"Blocking OCR finding {finding_id} must be fixed"
    if disposition == "fixed" and not (fields.get("commit") and fields.get("test")):
        return f"Fixed OCR finding {finding_id} needs commit and test evidence"
    if disposition == "deferred" and not fields.get("issue"):
        return f"Deferred OCR finding {finding_id} needs a linked issue"
    if disposition == "declined" and not fields.get("reason"):
        return f"Declined OCR finding {finding_id} needs a technical reason"
    return None


def validate_ocr_dispositions(head_sha, review_comments, issue_comments):
    dispositions = dispositions_by_finding(issue_comments)
    failures = []
    for finding in ocr_findings(head_sha, review_comments):
        finding_id = finding["id"]
        failure = disposition_error(
            finding_id,
            dispositions.get(finding_id, {}),
            bool(BLOCKING_RE.search(finding.get("body", ""))),
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


def read_json(path):
    return json.loads(Path(path).read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--review-comments", required=True)
    parser.add_argument("--issue-comments", required=True)
    parser.add_argument("--new-agent-label", action="append", default=[])
    parser.add_argument("--resolved-model-id")
    args = parser.parse_args()

    failures = validate_ocr_dispositions(
        args.head_sha,
        read_json(args.review_comments),
        read_json(args.issue_comments),
    )
    failures.extend(validate_agent_labels(args.new_agent_label, args.resolved_model_id))
    if failures:
        print("PR governance gate failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("PR governance gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
