#!/usr/bin/env python3
"""Validate evidence freshness and render a self-contained Chinese visit brief."""

from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


STATUS_LABELS = {
    "confirmed": ("已证实", "confirmed"),
    "company_claim": ("公司自述", "claim"),
    "analysis": ("分析判断", "analysis"),
    "unverified": ("未确认", "unverified"),
}

AUTHORITY_LABELS = {
    "official_record": "官方记录",
    "technical_primary": "技术原始资料",
    "company_primary": "公司一手口径",
    "counterparty": "交易/合作对手方",
    "reputable_media": "可信媒体",
    "aggregator": "聚合数据库",
    "weak": "弱来源",
}

ACCESS_LABELS = {
    "opened": "已打开核验",
    "snippet_only": "仅搜索摘要",
    "inaccessible": "页面不可访问",
}

FRESHNESS_LABELS = {
    "current": "当前可用",
    "historical": "历史证据",
    "stale": "已过时",
    "unknown": "时效未知",
}

TEMPORAL_SCOPES = {"current", "historical", "timeless"}
MATERIALITIES = {"critical", "supporting"}
FOUNDER_DIMENSIONS = {
    "identity_current_role": "身份与现任角色",
    "education_career": "教育与职业履历",
    "technical_track_record": "技术积累与成果",
    "entrepreneurship_execution": "创业与执行能力",
    "public_views": "公开观点与战略取向",
    "integrity_risk": "待核验事项与公共记录风险",
}
STRONG_AUTHORITIES = {
    "official_record",
    "technical_primary",
    "counterparty",
    "reputable_media",
}
PLACEHOLDER_MARKERS = ("TODO", "TBD", "Lorem ipsum", "示例科技")


def fail(message: str) -> None:
    raise ValueError(message)


def require_text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{path} must be a non-empty string")
    return value.strip()


def require_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{path} must be an array")
    return value


def require_bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        fail(f"{path} must be a boolean")
    return value


def parse_iso_date(value: Any, path: str, *, allow_empty: bool = False) -> date | None:
    if allow_empty and (value is None or value == ""):
        return None
    raw = require_text(value, path)
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        fail(f"{path} must use ISO YYYY-MM-DD: {exc}")


def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def parsed_web_url(value: Any) -> Any:
    raw = str(value or "").strip()
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return parsed


def is_search_results_url(parsed: Any) -> bool:
    host = parsed.hostname.lower() if parsed and parsed.hostname else ""
    path = parsed.path.lower() if parsed else ""
    if "google." in host and path.startswith("/search"):
        return True
    if host.endswith("bing.com") and path.startswith("/search"):
        return True
    if host.endswith("baidu.com") and path in {"/s", "/baidu"}:
        return True
    if host.endswith("duckduckgo.com") and path in {"/", "/html", "/lite"}:
        return True
    if host.endswith("search.yahoo.com"):
        return True
    return False


def safe_url(value: Any) -> str:
    parsed = parsed_web_url(value)
    if parsed and not is_search_results_url(parsed):
        return esc(str(value).strip())
    return ""


def scan_placeholders(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            scan_placeholders(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            scan_placeholders(item, f"{path}[{index}]")
    elif isinstance(value, str):
        marker = next((item for item in PLACEHOLDER_MARKERS if item.lower() in value.lower()), None)
        if marker:
            fail(f"{path} contains placeholder text: {marker}")


def validate(
    data: Any,
    *,
    today: date | None = None,
    max_research_age_days: int = 7,
    allow_stale_research: bool = False,
) -> dict[str, Any]:
    if not isinstance(data, dict):
        fail("root must be an object")
    if data.get("schema_version") != 3:
        fail("schema_version must equal 3; migrate the evidence ledger before rendering")
    if max_research_age_days < 0:
        fail("max_research_age_days must be non-negative")

    scan_placeholders(data)
    runtime_date = today or date.today()

    meta = data.get("meta")
    if not isinstance(meta, dict):
        fail("meta must be an object")
    require_text(meta.get("company_name"), "meta.company_name")
    research_date = parse_iso_date(meta.get("research_date"), "meta.research_date")
    cutoff_date = parse_iso_date(meta.get("information_cutoff"), "meta.information_cutoff")
    assert research_date is not None and cutoff_date is not None
    if research_date > runtime_date:
        fail("meta.research_date cannot be in the future")
    if cutoff_date > research_date:
        fail("meta.information_cutoff cannot be later than meta.research_date")
    research_age_days = (runtime_date - research_date).days
    cutoff_lag_days = (research_date - cutoff_date).days
    if not allow_stale_research and research_age_days > max_research_age_days:
        fail(
            f"research is {research_age_days} days old; maximum is {max_research_age_days}. "
            "Refresh sources or use --allow-stale-research only for a historical re-render"
        )
    if not allow_stale_research and cutoff_lag_days > max_research_age_days:
        fail(
            f"information cutoff lags research date by {cutoff_lag_days} days; "
            f"maximum is {max_research_age_days}"
        )

    verification = data.get("verification")
    if not isinstance(verification, dict):
        fail("verification must be an object")
    if not require_bool(verification.get("recent_search_completed"), "verification.recent_search_completed"):
        fail("verification.recent_search_completed must be true")
    if not require_bool(verification.get("identity_cross_checked"), "verification.identity_cross_checked"):
        fail("verification.identity_cross_checked must be true")
    claimed_cross_checks = verification.get("critical_claims_cross_checked")
    if isinstance(claimed_cross_checks, bool) or not isinstance(claimed_cross_checks, int):
        fail("verification.critical_claims_cross_checked must be an integer")
    limitations = require_list(verification.get("limitations"), "verification.limitations")
    for index, limitation in enumerate(limitations):
        require_text(limitation, f"verification.limitations[{index}]")

    founder_deep_dive = data.get("founder_deep_dive")
    if not isinstance(founder_deep_dive, dict):
        fail("founder_deep_dive must be an object")
    if not require_bool(founder_deep_dive.get("search_completed"), "founder_deep_dive.search_completed"):
        fail("founder_deep_dive.search_completed must be true")
    founder_limitations = require_list(
        founder_deep_dive.get("limitations"), "founder_deep_dive.limitations"
    )
    for index, limitation in enumerate(founder_limitations):
        require_text(limitation, f"founder_deep_dive.limitations[{index}]")
    founder_items = require_list(founder_deep_dive.get("items"), "founder_deep_dive.items")
    if len(founder_items) < len(FOUNDER_DIMENSIONS):
        fail(
            "founder_deep_dive.items must contain at least six claims covering all founder dimensions"
        )

    for key in ("executive_summary", "profile", "sections", "unknowns", "sources"):
        require_list(data.get(key), key)

    topics = require_list(data.get("talk_topics"), "talk_topics")
    questions = require_list(data.get("key_questions"), "key_questions")
    if len(topics) != 3:
        fail(f"talk_topics must contain exactly 3 items; got {len(topics)}")
    if len(questions) != 5:
        fail(f"key_questions must contain exactly 5 items; got {len(questions)}")

    source_map: dict[str, dict[str, Any]] = {}
    opened_sources = 0
    current_sources = 0
    access_failures = 0
    for index, source in enumerate(data["sources"]):
        path = f"sources[{index}]"
        if not isinstance(source, dict):
            fail(f"{path} must be an object")
        source_id = require_text(source.get("id"), f"{path}.id")
        if source_id in source_map:
            fail(f"duplicate source id: {source_id}")
        for key in ("title", "publisher", "type", "note"):
            require_text(source.get(key), f"{path}.{key}")
        parsed = parsed_web_url(source.get("url"))
        if not parsed:
            fail(f"{path}.url must be a final http or https URL")
        if is_search_results_url(parsed):
            fail(f"{path}.url must not be a search-results URL")

        published_at = parse_iso_date(source.get("published_at"), f"{path}.published_at", allow_empty=True)
        accessed_at = parse_iso_date(source.get("accessed_at"), f"{path}.accessed_at")
        assert accessed_at is not None
        if published_at and published_at > research_date:
            fail(f"{path}.published_at cannot be later than the research date")
        if accessed_at > research_date:
            fail(f"{path}.accessed_at cannot be later than the research date")
        if (research_date - accessed_at).days > max_research_age_days:
            fail(f"{path}.accessed_at is too old for this research run")

        authority = source.get("authority")
        access_status = source.get("access_status")
        freshness = source.get("freshness")
        if authority not in AUTHORITY_LABELS:
            fail(f"{path}.authority must be one of {', '.join(AUTHORITY_LABELS)}")
        if access_status not in ACCESS_LABELS:
            fail(f"{path}.access_status must be one of {', '.join(ACCESS_LABELS)}")
        if freshness not in FRESHNESS_LABELS:
            fail(f"{path}.freshness must be one of {', '.join(FRESHNESS_LABELS)}")
        if access_status != "opened" and freshness != "unknown":
            fail(f"{path}: snippet-only or inaccessible sources must use freshness=unknown")
        if freshness == "current" and access_status != "opened":
            fail(f"{path}: only an opened source can be current")
        if freshness == "current" and published_at and (research_date - published_at).days > 365:
            fail(f"{path}: a dated source older than 365 days cannot be marked current")

        if access_status == "opened":
            opened_sources += 1
        else:
            access_failures += 1
        if freshness == "current":
            current_sources += 1
        source_map[source_id] = source

    audited_cross_checks = 0

    def check_claim(claim: Any, path: str) -> None:
        nonlocal audited_cross_checks
        if not isinstance(claim, dict):
            fail(f"{path} must be an object")
        status = claim.get("evidence_status")
        temporal_scope = claim.get("temporal_scope")
        materiality = claim.get("materiality")
        if status not in STATUS_LABELS:
            fail(f"{path}.evidence_status must be one of {', '.join(STATUS_LABELS)}")
        if temporal_scope not in TEMPORAL_SCOPES:
            fail(f"{path}.temporal_scope must be one of {', '.join(sorted(TEMPORAL_SCOPES))}")
        if materiality not in MATERIALITIES:
            fail(f"{path}.materiality must be one of {', '.join(sorted(MATERIALITIES))}")
        as_of = parse_iso_date(claim.get("as_of"), f"{path}.as_of")
        assert as_of is not None
        if as_of > cutoff_date:
            fail(f"{path}.as_of cannot be later than meta.information_cutoff")

        citation_ids = claim.get("source_ids", [])
        if not isinstance(citation_ids, list):
            fail(f"{path}.source_ids must be an array")
        normalized_ids = [str(item) for item in citation_ids]
        if len(normalized_ids) != len(set(normalized_ids)):
            fail(f"{path}.source_ids contains duplicates")
        missing = [item for item in normalized_ids if item not in source_map]
        if missing:
            fail(f"{path} cites missing sources: {', '.join(missing)}")
        cited = [source_map[item] for item in normalized_ids]
        opened = [source for source in cited if source["access_status"] == "opened"]
        current = [source for source in opened if source["freshness"] == "current"]
        publishers = {str(source["publisher"]).strip().casefold() for source in opened}

        if status != "unverified" and not normalized_ids:
            fail(f"{path}: {status} claims require at least one source")
        if status == "confirmed":
            if not opened:
                fail(f"{path}: confirmed claims require an opened source")
            if not any(source["authority"] in STRONG_AUTHORITIES for source in opened):
                fail(f"{path}: company-only, aggregator-only, or weak evidence cannot be confirmed")
        elif status == "company_claim":
            if not any(source["authority"] == "company_primary" for source in opened):
                fail(f"{path}: company_claim requires an opened company_primary source")
        elif status == "analysis" and not opened:
            fail(f"{path}: analysis requires opened source inputs")

        if temporal_scope == "current" and status != "unverified" and not current:
            fail(f"{path}: a current claim requires an opened current source")

        if materiality == "critical" and status in {"confirmed", "analysis"}:
            evidence_pool = current if temporal_scope == "current" else opened
            pool_publishers = {str(source["publisher"]).strip().casefold() for source in evidence_pool}
            if len(evidence_pool) < 2 or len(pool_publishers) < 2:
                fail(f"{path}: a critical {status} claim requires two eligible sources from different publishers")
            audited_cross_checks += 1

    founder_dimensions_seen: set[str] = set()
    for index, item in enumerate(founder_items):
        path = f"founder_deep_dive.items[{index}]"
        if not isinstance(item, dict):
            fail(f"{path} must be an object")
        require_text(item.get("person"), f"{path}.person")
        require_text(item.get("label"), f"{path}.label")
        require_text(item.get("text"), f"{path}.text")
        dimension = item.get("dimension")
        if dimension not in FOUNDER_DIMENSIONS:
            fail(f"{path}.dimension must be one of {', '.join(FOUNDER_DIMENSIONS)}")
        founder_dimensions_seen.add(dimension)
        check_claim(item, path)
    missing_founder_dimensions = set(FOUNDER_DIMENSIONS) - founder_dimensions_seen
    if missing_founder_dimensions:
        fail(
            "founder_deep_dive.items is missing dimensions: "
            + ", ".join(sorted(missing_founder_dimensions))
        )

    for index, claim in enumerate(data["executive_summary"]):
        require_text(claim.get("text") if isinstance(claim, dict) else None, f"executive_summary[{index}].text")
        check_claim(claim, f"executive_summary[{index}]")
    for index, item in enumerate(data["profile"]):
        require_text(item.get("label") if isinstance(item, dict) else None, f"profile[{index}].label")
        require_text(item.get("value") if isinstance(item, dict) else None, f"profile[{index}].value")
        check_claim(item, f"profile[{index}]")
    for section_index, section in enumerate(data["sections"]):
        if not isinstance(section, dict):
            fail(f"sections[{section_index}] must be an object")
        require_text(section.get("title"), f"sections[{section_index}].title")
        items = require_list(section.get("items"), f"sections[{section_index}].items")
        for item_index, item in enumerate(items):
            require_text(
                item.get("text") if isinstance(item, dict) else None,
                f"sections[{section_index}].items[{item_index}].text",
            )
            check_claim(item, f"sections[{section_index}].items[{item_index}]")

    if claimed_cross_checks != audited_cross_checks:
        fail(
            "verification.critical_claims_cross_checked does not match the renderer audit: "
            f"declared {claimed_cross_checks}, computed {audited_cross_checks}"
        )
    if audited_cross_checks < 3 and not limitations:
        fail("verification.limitations must explain why fewer than 3 critical claims were cross-checked")

    for index, item in enumerate(data["unknowns"]):
        if not isinstance(item, dict):
            fail(f"unknowns[{index}] must be an object")
        for key in ("item", "impact", "next_check"):
            require_text(item.get(key), f"unknowns[{index}].{key}")
    for index, topic in enumerate(topics):
        if not isinstance(topic, dict):
            fail(f"talk_topics[{index}] must be an object")
        for key in ("title", "why", "opening", "listen_for"):
            require_text(topic.get(key), f"talk_topics[{index}].{key}")
    for index, question in enumerate(questions):
        if not isinstance(question, dict):
            fail(f"key_questions[{index}] must be an object")
        for key in ("question", "purpose", "positive_signal", "red_flag"):
            require_text(question.get(key), f"key_questions[{index}].{key}")

    data["_computed_audit"] = {
        "research_age_days": research_age_days,
        "opened_sources": opened_sources,
        "current_sources": current_sources,
        "access_failures": access_failures,
        "critical_claims_cross_checked": audited_cross_checks,
    }
    return data


def citations(source_ids: Any) -> str:
    links = []
    for source_id in source_ids or []:
        sid = str(source_id)
        links.append(f'<a class="cite" href="#source-{esc(sid)}">[{esc(sid)}]</a>')
    return "".join(links)


def status_badge(status: str) -> str:
    label, css_class = STATUS_LABELS[status]
    return f'<span class="badge {css_class}">{label}</span>'


def claim_audit(item: dict[str, Any]) -> str:
    critical = '<span class="mini-badge">关键判断</span>' if item.get("materiality") == "critical" else ""
    return f'{critical}<span class="as-of">截至 {esc(item.get("as_of", ""))}</span>'


def render_claim(item: dict[str, Any], show_label: bool = True) -> str:
    label = item.get("label", "")
    label_html = f'<strong class="claim-label">{esc(label)}</strong>' if show_label and label else ""
    return (
        '<li class="claim-item">'
        f'<div class="claim-head">{label_html}{status_badge(item["evidence_status"])}{claim_audit(item)}</div>'
        f'<div class="claim-text">{esc(item.get("text", ""))} {citations(item.get("source_ids"))}</div>'
        '</li>'
    )


def render(data: dict[str, Any]) -> str:
    meta = data["meta"]
    verification = data["verification"]
    audit = data["_computed_audit"]
    company = esc(meta["company_name"])
    legal_name = esc(meta.get("legal_name", ""))
    subtitle_bits = [bit for bit in (legal_name, esc(meta.get("visit_purpose", ""))) if bit]
    subtitle = " · ".join(subtitle_bits)

    summary_html = "".join(render_claim(item, show_label=False) for item in data["executive_summary"])

    founder_groups: dict[str, list[dict[str, Any]]] = {}
    for item in data["founder_deep_dive"]["items"]:
        founder_groups.setdefault(item["person"], []).append(item)
    founder_cards = []
    for person, items in founder_groups.items():
        claims = "".join(render_claim(item) for item in items)
        founder_cards.append(
            '<article class="founder-card">'
            f'<h3>{esc(person)}</h3><ul class="claim-list">{claims}</ul>'
            '</article>'
        )
    founder_limitations = data["founder_deep_dive"]["limitations"]
    founder_limitations_html = "".join(f'<li>{esc(item)}</li>' for item in founder_limitations)
    founder_limitations_block = (
        '<div class="founder-limitations"><b>创始人研究限制</b><ul>'
        f'{founder_limitations_html}</ul></div>'
        if founder_limitations
        else ""
    )
    founder_html = (
        '<section class="founder-priority"><div class="priority-kicker">FIRST · 核心人物判断</div>'
        '<h2>创始人深度画像（重点）</h2>'
        '<p class="section-summary">身份、履历、技术积累、创业执行、公开观点与待核验风险均按证据等级展示。</p>'
        f'<div class="founder-grid">{"".join(founder_cards)}</div>{founder_limitations_block}</section>'
    )

    profile_rows = []
    for item in data["profile"]:
        profile_rows.append(
            '<tr>'
            f'<th>{esc(item["label"])}</th>'
            f'<td>{esc(item["value"])} {citations(item.get("source_ids"))}<div>{claim_audit(item)}</div></td>'
            f'<td>{status_badge(item["evidence_status"])}</td>'
            '</tr>'
        )

    sections_html = []
    for section in data["sections"]:
        summary = section.get("summary", "")
        summary_block = f'<p class="section-summary">{esc(summary)}</p>' if summary else ""
        items = "".join(render_claim(item) for item in section["items"])
        sections_html.append(
            f'<section><h2>{esc(section["title"])}</h2>{summary_block}<ul class="claim-list">{items}</ul></section>'
        )

    unknown_rows = [
        '<tr>'
        f'<td>{esc(item["item"])}</td>'
        f'<td>{esc(item["impact"])}</td>'
        f'<td>{esc(item["next_check"])}</td>'
        '</tr>'
        for item in data["unknowns"]
    ]

    topics_html = []
    for index, topic in enumerate(data["talk_topics"], start=1):
        topics_html.append(
            '<article class="topic-card">'
            f'<div class="number">{index}</div><h3>{esc(topic["title"])}</h3>'
            f'<p><b>为什么聊：</b>{esc(topic["why"])}</p>'
            f'<p><b>自然开场：</b>“{esc(topic["opening"])}”</p>'
            f'<p><b>重点听：</b>{esc(topic["listen_for"])}</p>'
            '</article>'
        )

    questions_html = []
    for index, question in enumerate(data["key_questions"], start=1):
        questions_html.append(
            '<article class="question-card">'
            f'<div class="number">{index}</div><h3>{esc(question["question"])}</h3>'
            f'<p><b>验证目的：</b>{esc(question["purpose"])}</p>'
            '<div class="signal-grid">'
            f'<p class="positive"><b>积极信号</b><br>{esc(question["positive_signal"])}</p>'
            f'<p class="negative"><b>风险信号</b><br>{esc(question["red_flag"])}</p>'
            '</div></article>'
        )

    sources_html = []
    for source in data["sources"]:
        sid = esc(source["id"])
        url = safe_url(source["url"])
        title = esc(source["title"])
        title_html = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a>'
        date_bits = [str(source.get(key, "")).strip() for key in ("published_at", "accessed_at")]
        date_text = " / ".join(bit for bit in date_bits if bit)
        meta_bits = [source["publisher"], source["type"], date_text]
        source_meta = " · ".join(esc(bit) for bit in meta_bits if bit)
        source_audit = " · ".join(
            (
                AUTHORITY_LABELS[source["authority"]],
                ACCESS_LABELS[source["access_status"]],
                FRESHNESS_LABELS[source["freshness"]],
            )
        )
        sources_html.append(
            f'<li id="source-{sid}"><span class="source-id">[{sid}]</span> {title_html}'
            f'<div class="source-meta">{source_meta}</div>'
            f'<div class="source-audit">{esc(source_audit)}</div>'
            f'<div class="source-note">{esc(source["note"])}</div></li>'
        )

    limitations_html = "".join(f'<li>{esc(item)}</li>' for item in verification["limitations"])
    limitation_block = (
        f'<div class="limitations"><b>研究限制</b><ul>{limitations_html}</ul></div>' if limitations_html else ""
    )
    audit_html = (
        '<section class="audit-panel"><h2>证据与新鲜度审计</h2>'
        '<div class="audit-grid">'
        f'<div><b>{audit["research_age_days"]} 天</b><span>研究距今天数</span></div>'
        f'<div><b>{audit["opened_sources"]}</b><span>已打开来源</span></div>'
        f'<div><b>{audit["current_sources"]}</b><span>当前可用来源</span></div>'
        f'<div><b>{audit["critical_claims_cross_checked"]}</b><span>交叉核验关键判断</span></div>'
        f'<div><b>{audit["access_failures"]}</b><span>摘要/不可访问来源</span></div>'
        '</div>'
        f'{limitation_block}</section>'
    )

    identity_note = esc(meta.get("identity_note", ""))
    identity_html = f'<p class="identity-note">身份确认：{identity_note}</p>' if identity_note else ""
    unknowns_section = (
        '<section><h2>仍需现场确认</h2><div class="table-wrap"><table><thead><tr>'
        '<th>未知项</th><th>为什么重要</th><th>建议核验</th></tr></thead><tbody>'
        + "".join(unknown_rows)
        + '</tbody></table></div></section>'
        if unknown_rows
        else ""
    )

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{company}｜公司初访准备</title>
<style>
:root{{--ink:#1e2a24;--muted:#617067;--paper:#f3f7f3;--card:#fff;--line:#d8e8de;--green:#1f8f5f;--green-strong:#176f49;--green-mid:#36a66f;--green2:#e3f5ea;--amber:#8a5a00;--amber2:#fff0c9;--blue:#285d84;--blue2:#e6f0f8;--red:#9c3b32;--red2:#f9e5e2;}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font-family:"Noto Sans SC","Microsoft YaHei",system-ui,sans-serif;line-height:1.65}}
a{{color:var(--green);text-decoration:none}} a:hover{{text-decoration:underline}} .page{{max-width:1040px;margin:0 auto;padding:48px 28px 72px}}
.hero{{background:linear-gradient(135deg,#287f57 0%,#319b67 58%,#45ae78 100%);color:#fff;border-radius:24px;padding:42px;margin-bottom:24px;position:relative;overflow:hidden;box-shadow:0 16px 38px rgba(31,143,95,.16)}} .hero:after{{content:"";position:absolute;width:240px;height:240px;border-radius:50%;background:#9ae7b5;right:-90px;top:-110px;opacity:.34}}
.eyebrow{{font-size:13px;letter-spacing:.14em;color:#daf7e5;text-transform:uppercase}} h1{{font-size:42px;line-height:1.18;margin:12px 0 8px}} .subtitle{{color:#f0faf4;font-size:16px}} .meta{{display:flex;gap:16px;flex-wrap:wrap;margin-top:24px;color:#e8f7ee;font-size:13px}} .identity-note{{margin:14px 0 0;color:#d9eee2;font-size:13px}}
section{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:28px;margin-top:18px;box-shadow:0 8px 30px rgba(31,143,95,.055)}} h2{{font-size:22px;margin:0 0 16px;color:var(--green-strong)}} h3{{font-size:17px;margin:0 0 10px;color:var(--green-strong)}} .section-summary{{color:var(--muted);margin:-6px 0 18px}}
.audit-panel{{border-color:#b7dcc7;background:#f7fcf8}} .audit-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}} .audit-grid div{{border:1px solid var(--line);border-radius:12px;padding:14px;background:#fff}} .audit-grid b{{font-size:20px;display:block;color:var(--green-strong)}} .audit-grid span{{font-size:12px;color:var(--muted)}} .limitations{{margin-top:16px;color:#4d6357;font-size:13px}} .limitations ul{{margin:6px 0 0;padding-left:20px}}
.founder-priority{{border:2px solid #69c28d;background:linear-gradient(145deg,#f4fcf7 0%,#ffffff 72%);box-shadow:0 12px 34px rgba(31,143,95,.11);position:relative}} .founder-priority:before{{content:"";position:absolute;left:28px;right:28px;top:0;height:5px;background:linear-gradient(90deg,#36a66f,#65c98f,#9ae7b5);border-radius:0 0 6px 6px}} .priority-kicker{{font-size:11px;font-weight:700;letter-spacing:.14em;color:var(--green);margin-bottom:6px}} .founder-grid{{display:grid;gap:14px}} .founder-card{{border:1px solid #cbe8d6;border-radius:14px;padding:18px;background:#fff}} .founder-card h3{{font-size:20px;border-bottom:1px solid var(--line);padding-bottom:10px;margin-bottom:14px}} .founder-limitations{{margin-top:14px;padding:14px 16px;border-radius:12px;background:#edf8f1;color:#4d6357;font-size:13px}} .founder-limitations ul{{margin:6px 0 0;padding-left:20px}}
.claim-list{{list-style:none;padding:0;margin:0;display:grid;gap:12px}} .claim-item{{border-top:1px solid var(--line);padding-top:13px}} .claim-item:first-child{{border-top:0;padding-top:0}} .claim-head{{display:flex;align-items:center;gap:9px;margin-bottom:4px;flex-wrap:wrap}} .claim-label{{font-size:14px}} .claim-text{{color:#29352f}}
.badge{{font-size:11px;line-height:1;padding:5px 7px;border-radius:999px;white-space:nowrap}} .confirmed{{color:var(--green-strong);background:var(--green2)}} .badge.claim{{color:var(--amber);background:var(--amber2)}} .analysis{{color:var(--blue);background:var(--blue2)}} .unverified{{color:var(--red);background:var(--red2)}} .mini-badge{{font-size:10px;border:1px solid #8bc8a8;color:var(--green-strong);padding:2px 6px;border-radius:999px}} .as-of{{font-size:11px;color:var(--muted)}} .cite{{font-size:11px;margin-left:3px;vertical-align:super}}
.table-wrap{{overflow-x:auto}} table{{width:100%;border-collapse:collapse;font-size:14px}} th,td{{padding:12px 10px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}} th{{color:var(--muted);font-weight:600}} tbody tr:last-child th,tbody tr:last-child td{{border-bottom:0}}
.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}} .topic-card,.question-card{{border:1px solid var(--line);border-radius:14px;padding:18px;position:relative;background:linear-gradient(180deg,#fff 0%,#fbfefc 100%)}} .number{{width:28px;height:28px;border-radius:8px;background:var(--green);color:#fff;display:grid;place-items:center;font-weight:700;margin-bottom:14px;box-shadow:0 5px 12px rgba(31,143,95,.18)}} .topic-card p,.question-card p{{font-size:14px;margin:9px 0;color:#3b4842}}
.questions{{display:grid;grid-template-columns:1fr 1fr;gap:14px}} .question-card:last-child{{grid-column:1/-1}} .signal-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px}} .signal-grid p{{border-radius:10px;padding:10px}} .positive{{background:var(--green2)}} .negative{{background:var(--red2)}}
.sources{{font-size:13px}} .sources li{{margin:0 0 14px;padding-left:3px}} .source-id{{font-weight:700}} .source-meta,.source-note{{color:var(--muted);font-size:12px}} .source-audit{{color:var(--green);font-size:11px}} .legend{{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}}
footer{{color:var(--muted);font-size:12px;text-align:center;margin-top:28px}}
@media(max-width:760px){{.page{{padding:20px 14px 44px}}.hero{{padding:28px 22px;border-radius:18px}}h1{{font-size:31px}}section{{padding:20px}}.cards,.questions,.audit-grid{{grid-template-columns:1fr}}.question-card:last-child{{grid-column:auto}}.signal-grid{{grid-template-columns:1fr}}}}
@media print{{body{{background:#fff}}.page{{max-width:none;padding:0}}.hero{{border-radius:0;box-shadow:none}}section{{break-inside:avoid;box-shadow:none}}a{{color:inherit;text-decoration:none}}}}
</style>
</head>
<body><main class="page">
<header class="hero"><div class="eyebrow">Hard-tech company visit brief</div><h1>{company}</h1><div class="subtitle">{subtitle}</div><div class="meta"><span>研究日期：{esc(meta['research_date'])}</span><span>信息截止：{esc(meta['information_cutoff'])}</span></div>{identity_html}</header>
{founder_html}
{audit_html}
<section><h2>概括</h2><ul class="claim-list">{summary_html}</ul><div class="legend"><span class="badge confirmed">已证实</span><span class="badge claim">公司自述</span><span class="badge analysis">分析判断</span><span class="badge unverified">未确认</span></div></section>
<section><h2>公司画像</h2><div class="table-wrap"><table><tbody>{''.join(profile_rows)}</tbody></table></div></section>
{''.join(sections_html)}
{unknowns_section}
<section><h2>3个话题</h2><div class="cards">{''.join(topics_html)}</div></section>
<section><h2>5个问题</h2><div class="questions">{''.join(questions_html)}</div></section>
<section><h2>公开来源</h2><ol class="sources">{''.join(sources_html)}</ol></section>
<footer>本材料基于截至所示日期可访问的公开信息，用于初步拜访准备，不构成完整尽调、估值或法律意见。</footer>
</main></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="UTF-8 JSON input")
    parser.add_argument("--output", required=True, type=Path, help="HTML output path")
    parser.add_argument(
        "--max-research-age-days",
        type=int,
        default=7,
        help="Maximum allowed age of current research; default: 7",
    )
    parser.add_argument(
        "--allow-stale-research",
        action="store_true",
        help="Allow historical re-rendering; never use to present stale research as current",
    )
    args = parser.parse_args()

    try:
        with args.input.open("r", encoding="utf-8-sig") as handle:
            data = validate(
                json.load(handle),
                max_research_age_days=args.max_research_age_days,
                allow_stale_research=args.allow_stale_research,
            )
        output = render(data)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Wrote {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

