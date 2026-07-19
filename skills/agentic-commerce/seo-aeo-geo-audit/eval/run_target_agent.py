#!/usr/bin/env python3
"""Deterministic target-agent contract for the isolated SEO audit harness."""
import json
import os
from pathlib import Path


PROTOCOL_VERSION = "seo-aeo-geo-artifact-runner/v1"


def source_index(observations: list[dict]) -> dict[str, dict]:
    return {item["source"]: item for item in observations if isinstance(item, dict) and isinstance(item.get("source"), str)}


def is_audit_request(prompt: str, observations: list[dict]) -> bool:
    request = prompt.casefold()
    return any(word in request for word in ("audit", "review", "assess")) and not any(item.get("source") == "brief" or item.get("task") for item in observations if isinstance(item, dict))


def route_artifact(observations: list[dict]) -> dict:
    task = next((item.get("task", "") for item in observations if isinstance(item, dict)), "")
    routes = {
        "copy rewrite only": "seo-copy",
        "production deployment": "authorized-deployment",
        "paid advertising": "paid-acquisition",
        "metric calculation": "analytics",
        "refund authorization": "authorized-support-flow",
    }
    return {"disposition": "route", "route": routes.get(task, "general-assistance"), "findings": [], "recommendations": [], "evidence": [{"source": item["source"]} for item in observations if isinstance(item, dict) and isinstance(item.get("source"), str)]}


def audit_artifact(observations: list[dict]) -> dict:
    sources = source_index(observations)
    findings, recommendations, evidence = [], [], []

    def add(finding: str, recommendation: str, *evidence_sources: str) -> None:
        findings.append({"id": finding})
        recommendations.append({"id": recommendation})
        evidence.extend({"source": source} for source in evidence_sources)

    headers = next((item for source, item in sources.items() if source.startswith("headers:")), None)
    sitemap = sources.get("sitemap.xml", {})
    if headers and headers.get("canonical"):
        canonical = headers["canonical"]
        source_path = next(source.removeprefix("headers:") for source in sources if source.startswith("headers:"))
        if not canonical.endswith(source_path):
            add("canonical-mismatch", "align-canonical", next(source for source in sources if source.startswith("headers:")))
        if canonical not in sitemap.get("urls", []):
            add("sitemap-omission", "add-canonical-url-to-sitemap", next(source for source in sources if source.startswith("headers:")), "sitemap.xml")
        if "noindex" in headers.get("robots", ""):
            add("noindex-policy", "review-policy-indexability", next(source for source in sources if source.startswith("headers:")))
    robots = sources.get("robots.txt", {})
    bot_check = next((item for source, item in sources.items() if source.startswith("bot-check:")), {})
    rules = [rule.casefold() for rule in robots.get("rules", [])]
    if any("gptbot" in rule for rule in rules) and any("disallow" in rule for rule in rules) and bot_check.get("GPTBot_status") == 403:
        add("ai-crawler-blocked", "review-ai-crawler-policy", "robots.txt", next(source for source in sources if source.startswith("bot-check:")))
    page = next((item for source, item in sources.items() if source.startswith("page:")), {})
    html = next((item for source, item in sources.items() if source.startswith("html:")), {})
    if page.get("visible_claims") == [] and html.get("faq_count") == 0 and html.get("comparison_content") is False:
        add("answer-content-gap", "add-buyer-questions-and-comparisons", next(source for source in sources if source.startswith("page:")), next(source for source in sources if source.startswith("html:")))
    jsonld = next((item for source, item in sources.items() if source.startswith("jsonld:")), {})
    if page.get("visible_price") and jsonld.get("offer_price") and (page["visible_price"].split()[0] != jsonld["offer_price"] or page.get("visible_availability") != jsonld.get("offer_availability")):
        add("structured-data-offer-mismatch", "synchronize-product-offer-schema", next(source for source in sources if source.startswith("page:")), next(source for source in sources if source.startswith("jsonld:")))
    return {"disposition": "audit", "findings": findings, "recommendations": recommendations, "evidence": evidence}


def run(prompt: str, payload: dict, condition: str) -> dict:
    observations = payload.get("observations", [])
    use_skill = condition == "enabled" and is_audit_request(prompt, observations)
    artifact = audit_artifact(observations) if use_skill else route_artifact(observations)
    return {"protocol_version": PROTOCOL_VERSION, "skill_used": use_skill, "audit_artifact": artifact}


def main() -> int:
    case = json.loads((Path(os.environ.get("HARNESS_WORKSPACE", "/workspace")) / "case.json").read_text())
    print(json.dumps(run(case["prompt"], case["input"], os.environ["HARNESS_CONDITION"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
