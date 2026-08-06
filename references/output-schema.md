# HTML renderer data contract

Save one UTF-8 JSON object and pass it to `scripts/render_brief.py`.

## Top-level shape

```json
{
  "meta": {
    "company_name": "示例科技",
    "legal_name": "示例科技有限公司",
    "research_date": "2026-08-06",
    "information_cutoff": "2026-08-06",
    "visit_purpose": "一级投资人初步拜访",
    "identity_note": "已通过官网与公开注册信息交叉确认"
  },
  "executive_summary": [
    {
      "text": "公司面向……提供……，目前处于客户验证阶段。",
      "evidence_status": "confirmed",
      "source_ids": ["S01", "S03"]
    }
  ],
  "profile": [
    {
      "label": "成立时间",
      "value": "2021年",
      "evidence_status": "confirmed",
      "source_ids": ["S02"]
    }
  ],
  "sections": [
    {
      "title": "核心产品与技术",
      "summary": "一句话概括本节。",
      "items": [
        {
          "label": "客户问题",
          "text": "……",
          "evidence_status": "analysis",
          "source_ids": ["S01", "S04"]
        }
      ]
    }
  ],
  "unknowns": [
    {
      "item": "量产良率口径未公开",
      "impact": "影响成本与交付判断",
      "next_check": "拜访时询问最近三个批次的数据口径"
    }
  ],
  "talk_topics": [
    {
      "title": "技术路线与客户约束",
      "why": "理解差异化能否转化为采购理由",
      "opening": "我们看到贵司选择……，想了解客户最看重的约束是什么？",
      "listen_for": "是否能用客户指标、替代方案和权衡解释路线选择"
    }
  ],
  "key_questions": [
    {
      "question": "客户为什么愿意从现有方案切换？",
      "purpose": "验证痛点强度",
      "positive_signal": "能说明具体场景、预算主体和量化门槛",
      "red_flag": "只谈宏观市场或政策，不谈使用者"
    }
  ],
  "sources": [
    {
      "id": "S01",
      "title": "公司官网产品页",
      "publisher": "示例科技",
      "url": "https://example.com/product",
      "published_at": "2026-06-01",
      "accessed_at": "2026-08-06",
      "type": "公司官网",
      "note": "产品定位与参数；属于公司自述"
    }
  ]
}
```

## Required rules

- `meta.company_name`, `meta.research_date`, and `meta.information_cutoff` must be non-empty.
- `executive_summary`, `profile`, `sections`, `unknowns`, and `sources` are arrays. They may be short but must not contain placeholders.
- `talk_topics` must contain exactly 3 objects.
- `key_questions` must contain exactly 5 objects.
- Every cited ID must exist in `sources`.
- Use only `confirmed`, `company_claim`, `analysis`, or `unverified` for `evidence_status`.
- Use ISO dates where possible. If a publication date is unknown, use an empty string and explain in `note`.
- Use the final underlying `http` or `https` URL. Do not use a search-results URL.

## Recommended sections

Use four or five sections according to available evidence:

1. `公司在解决什么问题`
2. `核心产品与技术`
3. `工程化与商业化进展`
4. `团队、融资与组织信号`
5. `竞争位置与初步判断`

Keep claims atomic: one claim, one evidence status, and the relevant source IDs. Avoid embedding Markdown or HTML in any value; the renderer escapes all text.
