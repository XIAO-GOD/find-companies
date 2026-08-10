# Public-source research and freshness guide

## Research boundary

Research broadly, then write selectively. The output supports an initial investor visit, not full diligence. Never use model memory as evidence. Separate confirmed facts, company claims, analysis, and unknowns throughout.

## Two-pass workflow

### Pass 1: discovery

Search the legal name, brand, aliases, English name, founders, and flagship products. Build a candidate source list across identity, product, technology, team, financing, customers, commercialization, intellectual property, production, recruiting, competition, and risks.

### Pass 2: verification

Open the underlying page for every material claim. Record what the page actually supports, its publisher, publication date, access date, authority, access status, and freshness. Search explicitly for later updates before describing any fact as current.

A search result, cached preview, AI summary, inaccessible URL, or number of matching results is never evidence. Use it only to locate an underlying page.

## Source authority

Assign every source one `authority` value.

| Value | Typical sources | Proper use |
|---|---|---|
| `official_record` | regulator, exchange, court, government, registry, procurement, standards body | legal entity, filings, disclosed transactions, awards, penalties |
| `technical_primary` | patent, paper, standard, manual, test report, certification | technical design or measured evidence within its stated scope |
| `company_primary` | company website, official account, founder interview, product release, recruiting page | evidence of what the company says; not independent proof of performance |
| `counterparty` | customer, supplier, partner, investor announcement naming the company | concrete relationship or transaction within the counterparty's stated scope |
| `reputable_media` | dated, attributed financial, industry, or technology reporting | independent reporting; trace decisive claims to primary sources when possible |
| `aggregator` | company databases and data aggregators | discovery and weak corroboration only |
| `weak` | forums, reposts, anonymous social posts, search snippets | leads only; normally `unverified` |

Match the source to the claim. A patent proves that an application or grant exists, not that the product works. A partner announcement proves a stated cooperation, not an order or revenue. A company product page proves positioning, not benchmark superiority.

## Access and freshness

Assign every source an `access_status` and `freshness` value.

### Access status

- `opened`: the underlying page was opened and read during this research run.
- `snippet_only`: only a search result or cached snippet was available.
- `inaccessible`: the underlying URL could not be read because of a paywall, error, login, deletion, or network failure.

Only `opened` sources may support `confirmed`, `company_claim`, or `analysis`. Snippet-only and inaccessible sources may support only `unverified` leads.

### Freshness

- `current`: re-opened in this run and suitable for a current-state claim. For changing facts, prefer evidence published or explicitly updated within the last 180 days; extend to 365 days only when no later update exists and state the limitation.
- `historical`: reliable for a dated past event but not for the present state.
- `stale`: superseded, contradicted, or too old to describe the current state.
- `unknown`: the date or current applicability cannot be established.

An undated live official page can be `current` only when the page clearly represents the current product, team, or corporate state and was opened in this run. Explain the missing publication date in the note.

## Current-information search protocol

Read the system date before searching and use it as `research_date`. For every changing facet, run at least one explicit recency query using the current year, “最新”, “截至”, or a recent date range.

| Facet | Required recency check |
|---|---|
| Identity and management | official current page plus recent registry, filing, or attributed report |
| Product and technology stage | latest release, manual, test, conference, patent, or current product page |
| Financing and shareholders | latest announced round, investor disclosure, filing, or listed-company announcement |
| Customers and commercialization | latest customer, procurement, delivery, validation, or counterparty evidence |
| Capacity and delivery | latest facility, recruiting, certification, quality, or production signal |
| Competition | current competing products and substitute routes, not only historical market reports |
| Risks | recent regulator, court, recall, penalty, dispute, or delay searches |

Before finishing, run one final “company name + latest/current year” search to detect announcements published after the initial source set.

## Search matrix

| Facet | Typical queries and targets |
|---|---|
| Identity | 公司名 官网 / 法定全称 / 总部 / 成立 / 子公司 / English |
| Product | 公司名 产品 / 型号 / 参数 / 手册 / 发布 / 解决方案 / 当前年份 |
| Technology | 公司名 技术路线 / 专利 / 论文 / 测试 / 认证 / 标准 / benchmark |
| Team | 公司名 创始人 / 首席科学家 / 核心团队 / 离职 / 加入 / 当前年份 |
| Financing | 公司名 融资 / 投资方 / 轮次 / 金额 / 工商变更 / 当前年份 |
| Customers | 公司名 客户 / 中标 / 采购 / 验证 / 交付 / 定点 / 合作 |
| Capacity | 公司名 产线 / 扩产 / 基地 / 良率 / 产能 / 招聘 / 售后 |
| Competition | 产品类别 竞品 / 替代路线 / 国际厂商 / 国产化 / 市占率 |
| Risk | 公司名 诉讼 / 处罚 / 召回 / 失信 / 知识产权纠纷 / 延期 |

Use `site:` queries for official domains, government domains, exchanges, patent portals, procurement portals, counterparties, and reputable media. Cite the final page, never the search-results URL.

## Claim discipline

Make every claim atomic and assign:

- `evidence_status`: `confirmed`, `company_claim`, `analysis`, or `unverified`;
- `temporal_scope`: `current`, `historical`, or `timeless`;
- `materiality`: `critical` or `supporting`;
- `as_of`: the date through which the wording is valid.

Apply these rules:

- Use `confirmed` only when an opened source provides independent or authoritative support. Company-only evidence cannot be `confirmed`.
- Use `company_claim` when the claim originates from the company, founder, or controlled channel and lacks independent verification.
- Use `analysis` only for an explicit inference from cited facts. Show calculation inputs and formulas for numerical estimates.
- Use `unverified` for conflicting, snippet-only, inaccessible, anonymous, undated, or inadequately supported information.
- Cross-check every `critical` `confirmed` current claim with at least two opened current sources from different publishers. If this is impossible, downgrade it.
- Never invent revenue, valuation, market share, customer names, orders, yields, performance, production volume, or dates.
- Never turn “not found” into “does not exist.” Report the search limitation.

## Contradictions and superseded facts

Do not average or silently choose between conflicting claims.

1. Prefer the source with direct authority over the fact.
2. Prefer the later source only when it explicitly updates or supersedes the earlier state.
3. Preserve both facts when they describe different dates, entities, products, or definitions.
4. If the conflict remains unresolved, use `unverified`, state both versions, and convert the gap into a meeting question.

## Reverse claim audit

Audit the finished narrative from claim back to evidence:

1. Open the cited page again if needed.
2. Identify the exact sentence, table, filing item, or calculation input that supports the claim.
3. Check that the wording does not broaden the source's scope.
4. Check that the source is fresh enough for the temporal scope.
5. Check that company claims are visibly attributed.
6. Check that each critical confirmed current claim has two current publishers.
7. Remove or downgrade any claim that fails.

## Minimum coverage checklist

Attempt each item; mark unavailable items as unknown rather than omitting them silently.

- Exact entity and official web presence
- Product form, target customer, and customer's current alternative
- Technical route and one measurable differentiator
- Prototype, validation, delivery, or scale stage
- One concrete customer or partner journey, if publicly available
- Founders and current role coverage relevant to execution
- Latest disclosed financing history and current round, if any
- Principal competitors and substitute routes
- Intellectual-property, paper, certification, or standards evidence
- Manufacturing, delivery, quality, recruiting, or after-sales signals
- Material contradictions, stale claims, unsuccessful searches, and negative public signals

## Synthesis heuristic

Use the causal chain:

`technical indicator → stable product → customer validation → procurement reason → repeatable delivery → defensibility → next financing milestone`

Identify where the chain is supported, where it breaks, and what evidence would repair it. Select topics and questions from the weakest consequential links. When information is sparse, produce a shorter report with stronger unknowns. When information is abundant, compress repeated publicity and retain only decision-relevant evidence.
