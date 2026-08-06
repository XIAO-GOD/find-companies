#!/usr/bin/env python3
"""Validate structured visit research and render a self-contained Chinese HTML brief."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


STATUS_LABELS = {
    "confirmed": ("已证实", "confirmed"),
    "company_claim": ("公司自述", "claim"),
    "analysis": ("分析判断", "analysis"),
    "unverified": ("未确认", "unverified"),
}


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


def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def safe_url(value: Any) -> str:
    raw = str(value or "").strip()
    parsed = urlparse(raw)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return esc(raw)
    return ""


def validate(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        fail("root must be an object")

    meta = data.get("meta")
    if not isinstance(meta, dict):
        fail("meta must be an object")
    for key in ("company_name", "research_date", "information_cutoff"):
        require_text(meta.get(key), f"meta.{key}")

    for key in ("executive_summary", "profile", "sections", "unknowns", "sources"):
        require_list(data.get(key), key)

    topics = require_list(data.get("talk_topics"), "talk_topics")
    questions = require_list(data.get("key_questions"), "key_questions")
    if len(topics) != 3:
        fail(f"talk_topics must contain exactly 3 items; got {len(topics)}")
    if len(questions) != 5:
        fail(f"key_questions must contain exactly 5 items; got {len(questions)}")

    source_ids: set[str] = set()
    for index, source in enumerate(data["sources"]):
        if not isinstance(source, dict):
            fail(f"sources[{index}] must be an object")
        source_id = require_text(source.get("id"), f"sources[{index}].id")
        if source_id in source_ids:
            fail(f"duplicate source id: {source_id}")
        source_ids.add(source_id)

    def check_claim(claim: Any, path: str) -> None:
        if not isinstance(claim, dict):
            fail(f"{path} must be an object")
        status = claim.get("evidence_status")
        if status not in STATUS_LABELS:
            fail(f"{path}.evidence_status must be one of {', '.join(STATUS_LABELS)}")
        citation_ids = claim.get("source_ids", [])
        if not isinstance(citation_ids, list):
            fail(f"{path}.source_ids must be an array")
        missing = [str(item) for item in citation_ids if str(item) not in source_ids]
        if missing:
            fail(f"{path} cites missing sources: {', '.join(missing)}")

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


def render_claim(item: dict[str, Any], show_label: bool = True) -> str:
    label = item.get("label", "")
    label_html = f'<strong class="claim-label">{esc(label)}</strong>' if show_label and label else ""
    return (
        '<li class="claim-item">'
        f'<div class="claim-head">{label_html}{status_badge(item["evidence_status"])}</div>'
        f'<div class="claim-text">{esc(item.get("text", ""))} {citations(item.get("source_ids"))}</div>'
        '</li>'
    )


def render(data: dict[str, Any]) -> str:
    meta = data["meta"]
    company = esc(meta["company_name"])
    legal_name = esc(meta.get("legal_name", ""))
    subtitle_bits = [bit for bit in (legal_name, esc(meta.get("visit_purpose", ""))) if bit]
    subtitle = " · ".join(subtitle_bits)

    summary_html = "".join(render_claim(item, show_label=False) for item in data["executive_summary"])

    profile_rows = []
    for item in data["profile"]:
        profile_rows.append(
            '<tr>'
            f'<th>{esc(item["label"])}</th>'
            f'<td>{esc(item["value"])} {citations(item.get("source_ids"))}</td>'
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

    unknown_rows = []
    for item in data["unknowns"]:
        if not isinstance(item, dict):
            continue
        unknown_rows.append(
            '<tr>'
            f'<td>{esc(item.get("item", ""))}</td>'
            f'<td>{esc(item.get("impact", ""))}</td>'
            f'<td>{esc(item.get("next_check", ""))}</td>'
            '</tr>'
        )

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
        sid = esc(source.get("id", ""))
        url = safe_url(source.get("url", ""))
        title = esc(source.get("title", "未命名来源"))
        title_html = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a>' if url else title
        date_bits = [str(source.get(key, "")).strip() for key in ("published_at", "accessed_at")]
        date_text = " / ".join(bit for bit in date_bits if bit)
        meta_bits = [source.get("publisher", ""), source.get("type", ""), date_text]
        source_meta = " · ".join(esc(bit) for bit in meta_bits if bit)
        note = esc(source.get("note", ""))
        note_html = f'<div class="source-note">{note}</div>' if note else ""
        sources_html.append(
            f'<li id="source-{sid}"><span class="source-id">[{sid}]</span> {title_html}'
            f'<div class="source-meta">{source_meta}</div>{note_html}</li>'
        )

    identity_note = esc(meta.get("identity_note", ""))
    identity_html = f'<p class="identity-note">身份确认：{identity_note}</p>' if identity_note else ""
    unknowns_section = (
        '<section><h2>仍需现场确认</h2><div class="table-wrap"><table><thead><tr>'
        '<th>未知项</th><th>为什么重要</th><th>建议核验</th></tr></thead><tbody>'
        + "".join(unknown_rows)
        + '</tbody></table></div></section>'
        if unknown_rows else ""
    )

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{company}｜公司初访准备</title>
<style>
:root{{--ink:#17211d;--muted:#66736d;--paper:#f5f5f0;--card:#fff;--line:#dfe5e1;--green:#0d6b4f;--green2:#dff2e9;--amber:#8a5a00;--amber2:#fff0c9;--blue:#285d84;--blue2:#e6f0f8;--red:#9c3b32;--red2:#f9e5e2;}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font-family:"Noto Sans SC","Microsoft YaHei",system-ui,sans-serif;line-height:1.65}}
a{{color:var(--green);text-decoration:none}} a:hover{{text-decoration:underline}} .page{{max-width:1040px;margin:0 auto;padding:48px 28px 72px}}
.hero{{background:var(--ink);color:#fff;border-radius:24px;padding:42px;margin-bottom:24px;position:relative;overflow:hidden}} .hero:after{{content:"";position:absolute;width:240px;height:240px;border-radius:50%;background:#2c8b6d;right:-90px;top:-110px;opacity:.45}}
.eyebrow{{font-size:13px;letter-spacing:.14em;color:#a8d9c8;text-transform:uppercase}} h1{{font-size:42px;line-height:1.18;margin:12px 0 8px}} .subtitle{{color:#cbd6d1;font-size:16px}} .meta{{display:flex;gap:16px;flex-wrap:wrap;margin-top:24px;color:#dce5e1;font-size:13px}} .identity-note{{margin:14px 0 0;color:#b8c9c2;font-size:13px}}
section{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:28px;margin-top:18px;box-shadow:0 8px 30px rgba(23,33,29,.035)}} h2{{font-size:22px;margin:0 0 16px}} h3{{font-size:17px;margin:0 0 10px}} .section-summary{{color:var(--muted);margin:-6px 0 18px}}
.claim-list{{list-style:none;padding:0;margin:0;display:grid;gap:12px}} .claim-item{{border-top:1px solid var(--line);padding-top:13px}} .claim-item:first-child{{border-top:0;padding-top:0}} .claim-head{{display:flex;align-items:center;gap:9px;margin-bottom:4px}} .claim-label{{font-size:14px}} .claim-text{{color:#29352f}}
.badge{{font-size:11px;line-height:1;padding:5px 7px;border-radius:999px;white-space:nowrap}} .confirmed{{color:var(--green);background:var(--green2)}} .badge.claim{{color:var(--amber);background:var(--amber2)}} .analysis{{color:var(--blue);background:var(--blue2)}} .unverified{{color:var(--red);background:var(--red2)}} .cite{{font-size:11px;margin-left:3px;vertical-align:super}}
.table-wrap{{overflow-x:auto}} table{{width:100%;border-collapse:collapse;font-size:14px}} th,td{{padding:12px 10px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}} th{{color:var(--muted);font-weight:600}} tbody tr:last-child th,tbody tr:last-child td{{border-bottom:0}}
.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}} .topic-card,.question-card{{border:1px solid var(--line);border-radius:14px;padding:18px;position:relative}} .number{{width:28px;height:28px;border-radius:8px;background:var(--ink);color:#fff;display:grid;place-items:center;font-weight:700;margin-bottom:14px}} .topic-card p,.question-card p{{font-size:14px;margin:9px 0;color:#3b4842}}
.questions{{display:grid;grid-template-columns:1fr 1fr;gap:14px}} .question-card:last-child{{grid-column:1/-1}} .signal-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px}} .signal-grid p{{border-radius:10px;padding:10px}} .positive{{background:var(--green2)}} .negative{{background:var(--red2)}}
.sources{{font-size:13px}} .sources li{{margin:0 0 14px;padding-left:3px}} .source-id{{font-weight:700}} .source-meta,.source-note{{color:var(--muted);font-size:12px}} .legend{{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}}
footer{{color:var(--muted);font-size:12px;text-align:center;margin-top:28px}}
@media(max-width:760px){{.page{{padding:20px 14px 44px}}.hero{{padding:28px 22px;border-radius:18px}}h1{{font-size:31px}}section{{padding:20px}}.cards,.questions{{grid-template-columns:1fr}}.question-card:last-child{{grid-column:auto}}.signal-grid{{grid-template-columns:1fr}}}}
@media print{{body{{background:#fff}}.page{{max-width:none;padding:0}}.hero{{border-radius:0;box-shadow:none}}section{{break-inside:avoid;box-shadow:none}}a{{color:inherit;text-decoration:none}}}}
</style>
</head>
<body><main class="page">
<header class="hero"><div class="eyebrow">Hard-tech company visit brief</div><h1>{company}</h1><div class="subtitle">{subtitle}</div><div class="meta"><span>研究日期：{esc(meta['research_date'])}</span><span>信息截止：{esc(meta['information_cutoff'])}</span></div>{identity_html}</header>
<section><h2>先看结论</h2><ul class="claim-list">{summary_html}</ul><div class="legend"><span class="badge confirmed">已证实</span><span class="badge claim">公司自述</span><span class="badge analysis">分析判断</span><span class="badge unverified">未确认</span></div></section>
<section><h2>公司画像</h2><div class="table-wrap"><table><tbody>{''.join(profile_rows)}</tbody></table></div></section>
{''.join(sections_html)}
{unknowns_section}
<section><h2>建议聊的 3 个话题</h2><div class="cards">{''.join(topics_html)}</div></section>
<section><h2>要问公司的 5 个关键问题</h2><div class="questions">{''.join(questions_html)}</div></section>
<section><h2>公开来源</h2><ol class="sources">{''.join(sources_html)}</ol></section>
<footer>本材料基于公开信息，用于初步拜访准备，不构成完整尽调、估值或法律意见。</footer>
</main></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="UTF-8 JSON input")
    parser.add_argument("--output", required=True, type=Path, help="HTML output path")
    args = parser.parse_args()

    try:
        with args.input.open("r", encoding="utf-8-sig") as handle:
            data = validate(json.load(handle))
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
