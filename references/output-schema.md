# HTML renderer data contract

Save one UTF-8 JSON object and pass it to `scripts/render_brief.py`. Schema version 3 retains the deterministic evidence and freshness gates and adds a mandatory, first-position founder deep dive.

## Top-level shape

```json
{
  "schema_version": 3,
  "meta": {
    "company_name": "示例科技",
    "legal_name": "示例科技有限公司",
    "research_date": "2026-08-10",
    "information_cutoff": "2026-08-10",
    "visit_purpose": "一级投资人初步拜访",
    "identity_note": "已通过官网与公开注册信息交叉确认"
  },
  "verification": {
    "recent_search_completed": true,
    "identity_cross_checked": true,
    "critical_claims_cross_checked": 1,
    "limitations": [
      "公开信息不足以交叉验证三个关键现状判断，未验证内容已降级展示"
    ]
  },
  "founder_deep_dive": {
    "search_completed": true,
    "limitations": [
      "未找到可独立核验的完整履历，已将缺口转为现场问题"
    ],
    "items": [
      {
        "person": "张三",
        "dimension": "identity_current_role",
        "label": "身份与现任角色",
        "text": "公司官网称张三为创始人兼CEO。",
        "evidence_status": "company_claim",
        "temporal_scope": "current",
        "materiality": "critical",
        "as_of": "2026-08-10",
        "source_ids": ["S01"]
      },
      {
        "person": "张三",
        "dimension": "education_career",
        "label": "教育与职业履历",
        "text": "公开来源未形成可连续核验的教育与任职时间线。",
        "evidence_status": "unverified",
        "temporal_scope": "current",
        "materiality": "supporting",
        "as_of": "2026-08-10",
        "source_ids": []
      }
    ]
  },
  "executive_summary": [
    {
      "text": "截至2026年8月，公司产品处于客户验证阶段。",
      "evidence_status": "confirmed",
      "temporal_scope": "current",
      "materiality": "critical",
      "as_of": "2026-08-10",
      "source_ids": ["S01", "S02"]
    }
  ],
  "profile": [
    {
      "label": "成立时间",
      "value": "2021年",
      "evidence_status": "confirmed",
      "temporal_scope": "historical",
      "materiality": "supporting",
      "as_of": "2021-06-01",
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
          "text": "现有方案在功耗与部署密度之间存在权衡。",
          "evidence_status": "analysis",
          "temporal_scope": "current",
          "materiality": "supporting",
          "as_of": "2026-08-10",
          "source_ids": ["S01", "S02"]
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
      "published_at": "2026-07-01",
      "accessed_at": "2026-08-10",
      "type": "公司官网",
      "authority": "company_primary",
      "access_status": "opened",
      "freshness": "current",
      "note": "产品定位与参数；属于公司自述"
    },
    {
      "id": "S02",
      "title": "客户验证公告",
      "publisher": "示例客户",
      "url": "https://customer.example.com/news/validation",
      "published_at": "2026-08-01",
      "accessed_at": "2026-08-10",
      "type": "客户公告",
      "authority": "counterparty",
      "access_status": "opened",
      "freshness": "current",
      "note": "客户确认验证阶段，但未披露采购金额"
    }
  ]
}
```

The abbreviated founder example shows two dimensions for readability. Production input must cover all six founder dimensions and still contain exactly 3 topics and 5 questions.

## Required top-level rules

- `schema_version` must equal `3`.
- `meta.company_name`, `meta.research_date`, and `meta.information_cutoff` must be non-empty.
- Dates use ISO `YYYY-MM-DD`. Future research, cutoff, access, publication, or claim dates are rejected.
- `information_cutoff` cannot be later than `research_date`.
- The renderer rejects research older than 7 days by default. Change the limit with `--max-research-age-days`; use `--allow-stale-research` only for an explicitly historical re-render.
- `verification.recent_search_completed` and `verification.identity_cross_checked` must be `true`.
- `verification.critical_claims_cross_checked` must exactly equal the count independently computed by the renderer.
- `verification.limitations` is an array of explicit research limitations. If fewer than 3 critical claims are cross-checked, at least one limitation is required.
- `founder_deep_dive` is required. `search_completed` must be `true`; `limitations` and `items` are arrays.
- `founder_deep_dive.items` must contain at least six evidence-audited claims and collectively cover exactly these required dimensions: `identity_current_role`, `education_career`, `technical_track_record`, `entrepreneurship_execution`, `public_views`, and `integrity_risk`.
- Every founder item includes non-empty `person`, `dimension`, `label`, and `text`, plus all ordinary claim fields. Use `unverified` with an explicit search gap when a dimension has no reliable public evidence.
- `executive_summary`, `profile`, `sections`, `unknowns`, and `sources` are arrays and must not contain placeholders.
- `talk_topics` contains exactly 3 objects; `key_questions` contains exactly 5 objects.

## Claim rules

Every object in `founder_deep_dive.items`, `executive_summary`, `profile`, and `sections[].items` includes:

- `evidence_status`: `confirmed`, `company_claim`, `analysis`, or `unverified`;
- `temporal_scope`: `current`, `historical`, or `timeless`;
- `materiality`: `critical` or `supporting`;
- `as_of`: ISO date no later than `information_cutoff`;
- `source_ids`: an array of IDs that exist in `sources`.

Validation rules:

- `confirmed` requires at least one opened independent or authoritative source. Company-only, aggregator-only, weak, snippet-only, or inaccessible evidence cannot be confirmed.
- `company_claim` requires an opened `company_primary` source.
- `analysis` requires opened source inputs; critical analysis requires at least two opened sources.
- A non-unverified `current` claim requires at least one opened source marked `current`.
- A critical confirmed claim requires at least two opened sources from different publishers. If it is current, both must be marked `current`.
- `unverified` may have no source or may cite snippet-only/inaccessible leads.
- Keep claims atomic. Do not embed Markdown or HTML in values.

## Source rules

Every source includes:

- `authority`: `official_record`, `technical_primary`, `company_primary`, `counterparty`, `reputable_media`, `aggregator`, or `weak`;
- `access_status`: `opened`, `snippet_only`, or `inaccessible`;
- `freshness`: `current`, `historical`, `stale`, or `unknown`;
- `published_at`: ISO date or an empty string when unknown, with the missing date explained in `note`;
- `accessed_at`: ISO date from the current research run;
- a final underlying `http` or `https` URL, never a search-results URL.

Only an `opened` source may be marked `current`, `historical`, or `stale`. Snippet-only and inaccessible sources must use `unknown`.

## Recommended sections

The renderer always places `创始人深度画像（重点）` immediately after the cover and before the evidence audit and summary. Then use four or five company sections according to available evidence:

1. `公司在解决什么问题`
2. `核心产品与技术`
3. `工程化与商业化进展`
4. `团队、融资与组织信号`
5. `竞争位置与初步判断`

