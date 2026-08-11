#!/usr/bin/env python3
"""Regression tests for evidence and freshness validation."""

from __future__ import annotations

import unittest
from datetime import date

from render_brief import render, validate


def claim(
    text: str,
    status: str,
    scope: str,
    materiality: str,
    source_ids: list[str],
    *,
    as_of: str = "2026-08-10",
) -> dict[str, object]:
    return {
        "text": text,
        "evidence_status": status,
        "temporal_scope": scope,
        "materiality": materiality,
        "as_of": as_of,
        "source_ids": source_ids,
    }


def valid_data() -> dict[str, object]:
    topics = [
        {
            "title": f"话题{i}",
            "why": "验证因果关系",
            "opening": "想了解这一判断背后的客户约束。",
            "listen_for": "量化指标、替代方案和失败条件",
        }
        for i in range(1, 4)
    ]
    questions = [
        {
            "question": f"关键问题{i}是什么？",
            "purpose": "验证关键假设",
            "positive_signal": "回答具体且可核验",
            "red_flag": "只给宏观描述",
        }
        for i in range(1, 6)
    ]
    return {
        "schema_version": 2,
        "meta": {
            "company_name": "星云芯片",
            "legal_name": "星云芯片有限公司",
            "research_date": "2026-08-10",
            "information_cutoff": "2026-08-10",
            "visit_purpose": "一级投资人初步拜访",
            "identity_note": "已通过两个不同来源交叉确认",
        },
        "verification": {
            "recent_search_completed": True,
            "identity_cross_checked": True,
            "critical_claims_cross_checked": 3,
            "limitations": [],
        },
        "executive_summary": [
            claim("产品处于客户验证阶段。", "confirmed", "current", "critical", ["S02", "S03"])
        ],
        "profile": [
            {
                "label": "成立时间",
                "value": "2022年",
                "evidence_status": "confirmed",
                "temporal_scope": "historical",
                "materiality": "supporting",
                "as_of": "2022-05-01",
                "source_ids": ["S04"],
            }
        ],
        "sections": [
            {
                "title": "核心产品与技术",
                "summary": "区分事实与推断。",
                "items": [
                    {
                        "label": "客户约束",
                        **claim("客户约束可能来自功耗。", "analysis", "current", "critical", ["S01", "S02"]),
                    },
                    {
                        "label": "验证进展",
                        **claim("两方均披露了验证。", "confirmed", "current", "critical", ["S02", "S03"]),
                    },
                ],
            }
        ],
        "unknowns": [
            {"item": "良率未公开", "impact": "影响成本判断", "next_check": "询问最近批次数据"}
        ],
        "talk_topics": topics,
        "key_questions": questions,
        "sources": [
            {
                "id": "S01",
                "title": "公司产品页",
                "publisher": "星云芯片",
                "url": "https://company.example.com/product",
                "published_at": "2026-07-01",
                "accessed_at": "2026-08-10",
                "type": "公司官网",
                "authority": "company_primary",
                "access_status": "opened",
                "freshness": "current",
                "note": "公司当前产品口径",
            },
            {
                "id": "S02",
                "title": "客户验证公告",
                "publisher": "客户甲",
                "url": "https://customer.example.com/validation",
                "published_at": "2026-08-01",
                "accessed_at": "2026-08-10",
                "type": "客户公告",
                "authority": "counterparty",
                "access_status": "opened",
                "freshness": "current",
                "note": "确认进入验证阶段",
            },
            {
                "id": "S03",
                "title": "产业报道",
                "publisher": "产业媒体",
                "url": "https://media.example.com/report",
                "published_at": "2026-08-02",
                "accessed_at": "2026-08-10",
                "type": "媒体报道",
                "authority": "reputable_media",
                "access_status": "opened",
                "freshness": "current",
                "note": "具名记者报道验证进展",
            },
            {
                "id": "S04",
                "title": "设立登记",
                "publisher": "市场监管部门",
                "url": "https://registry.example.com/company",
                "published_at": "2022-05-01",
                "accessed_at": "2026-08-10",
                "type": "官方登记",
                "authority": "official_record",
                "access_status": "opened",
                "freshness": "historical",
                "note": "支持历史成立时间",
            },
        ],
    }


class EvidenceGateTests(unittest.TestCase):
    def check(self, data: dict[str, object]) -> dict[str, object]:
        return validate(data, today=date(2026, 8, 10))

    def test_valid_data_renders_audit(self) -> None:
        data = self.check(valid_data())
        output = render(data)
        self.assertIn("证据与新鲜度审计", output)
        self.assertIn("交叉核验关键判断", output)
        self.assertIn("<h2>概括</h2>", output)
        self.assertNotIn("先看结论", output)
        self.assertIn("<h2>3个话题</h2>", output)
        self.assertNotIn("建议聊的 3 个话题", output)
        self.assertIn("<h2>5个问题</h2>", output)
        self.assertNotIn("要问公司的 5 个关键问题", output)

    def test_old_schema_is_rejected(self) -> None:
        data = valid_data()
        data.pop("schema_version")
        with self.assertRaisesRegex(ValueError, "schema_version"):
            self.check(data)

    def test_stale_research_is_rejected(self) -> None:
        data = valid_data()
        data["meta"]["research_date"] = "2026-07-01"
        data["meta"]["information_cutoff"] = "2026-07-01"
        with self.assertRaisesRegex(ValueError, "research is"):
            self.check(data)

    def test_future_source_date_is_rejected(self) -> None:
        data = valid_data()
        data["sources"][1]["published_at"] = "2026-08-11"
        with self.assertRaisesRegex(ValueError, "published_at"):
            self.check(data)

    def test_old_dated_source_cannot_be_current(self) -> None:
        data = valid_data()
        data["sources"][1]["published_at"] = "2025-08-09"
        with self.assertRaisesRegex(ValueError, "older than 365 days"):
            self.check(data)

    def test_search_results_url_is_rejected(self) -> None:
        data = valid_data()
        data["sources"][1]["url"] = "https://www.google.com/search?q=company"
        with self.assertRaisesRegex(ValueError, "search-results"):
            self.check(data)

    def test_company_only_confirmed_claim_is_rejected(self) -> None:
        data = valid_data()
        data["executive_summary"][0] = claim(
            "公司自称产品已量产。", "confirmed", "current", "supporting", ["S01"]
        )
        data["verification"]["critical_claims_cross_checked"] = 2
        data["verification"]["limitations"] = ["一项关键判断仅有公司口径"]
        with self.assertRaisesRegex(ValueError, "company-only"):
            self.check(data)

    def test_snippet_cannot_cross_check_current_claim(self) -> None:
        data = valid_data()
        data["sources"][1]["access_status"] = "snippet_only"
        data["sources"][1]["freshness"] = "unknown"
        with self.assertRaisesRegex(ValueError, "two eligible sources"):
            self.check(data)

    def test_declared_cross_check_count_must_match(self) -> None:
        data = valid_data()
        data["verification"]["critical_claims_cross_checked"] = 4
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.check(data)

    def test_company_claim_with_attribution_passes(self) -> None:
        data = valid_data()
        data["executive_summary"][0] = claim(
            "公司称产品处于客户验证阶段。", "company_claim", "current", "critical", ["S01"]
        )
        data["verification"]["critical_claims_cross_checked"] = 2
        data["verification"]["limitations"] = ["客户验证阶段缺少两方独立确认"]
        self.check(data)

    def test_exact_question_count_is_enforced(self) -> None:
        data = valid_data()
        data["key_questions"].pop()
        with self.assertRaisesRegex(ValueError, "exactly 5"):
            self.check(data)


if __name__ == "__main__":
    unittest.main()
