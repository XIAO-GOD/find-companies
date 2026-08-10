---
name: prepare-hardtech-company-visit
description: Research a named hard-technology company from current public web sources and create an evidence-gated, source-linked Chinese HTML briefing for an investor's first visit. Verifies company identity, checks information freshness, separates confirmed facts from company claims and analysis, exposes contradictions and unknowns, and outputs exactly 3 tailored conversation topics plus exactly 5 critical questions. Use for 公司拜访准备、初访公司、公司画像、全网搜索公司、最新情况、聊什么、问什么 or 生成拜访HTML across semiconductors, advanced manufacturing, new materials, robotics, AI infrastructure, aerospace, quantum, energy, biotech tools, and other hard-tech sectors. Do not use for full due diligence, valuation modeling, or legal opinions unless separately requested.
---

# Prepare a Hard-Tech Company Visit

## Goal

Turn current public-source research into a compact first-visit briefing without presenting model memory, stale publicity, or search snippets as facts. Help the investor understand what the company does, whether it merits continued attention, and what to learn next. Keep the meeting exploratory rather than interrogative.

## Inputs and defaults

Require a company name. Use optional user context such as location, product, website, meeting participants, fund thesis, or visit date when provided.

- Resolve the exact legal entity and brand before researching. If multiple plausible companies remain and choosing one could materially change the result, ask one concise disambiguation question.
- Read the system date before searching. Use it as `research_date`; never infer “latest” from model memory.
- Default language: Chinese.
- Default output: one self-contained `.html` file plus a one-paragraph handoff message.
- Default purpose: preliminary investor visit, not detailed due diligence.
- Honor active workspace policies. Otherwise save to the user's requested location or a sensible `output/` directory.

## Workflow

### 1. Frame three preliminary decisions

Research to answer:

1. What does the company actually sell, to whom, and for what problem?
2. What stage has the technology and product reached: concept, prototype, engineering sample, customer validation, initial delivery, or repeatable scale?
3. What should the investor clarify in the first visit before deciding whether to follow up?

Do not attempt a complete financial, legal, patent-validity, or customer-contract verification unless requested.

### 2. Resolve company identity

Establish the brand name, legal name, aliases, headquarters, founding year, official website, and core business. Search both Chinese and English names. Separate similarly named entities and subsidiaries.

Record identity uncertainty explicitly. Never merge facts from two entities because their names are similar.

### 3. Conduct broad public-source research

Read [references/research-guide.md](references/research-guide.md) before searching. Cover identity, product and technology, team, financing, customers and commercialization, intellectual property or papers, production and recruiting signals, competition, and material negative signals.

Use the best available web search and page-reading tools. Run both broad discovery queries and date-bounded “latest/current” queries. Open the underlying page for every cited material claim. Model memory, search-result snippets, cached previews, and an inaccessible URL are leads only. If network research tools are unavailable, state the limitation and do not fabricate a briefing.

### 4. Lock the time scope and verify freshness

Follow [references/research-guide.md](references/research-guide.md) for freshness windows, source authority, contradiction handling, and the reverse claim audit.

- Re-open sources during the current run; record access dates.
- For financing, management, product stage, customers, orders, capacity, litigation, and other changing facts, locate the newest dated evidence and search explicitly for later updates.
- Mark older but valid event records as `historical`; never use them alone to describe the current state.
- If a current claim cannot be supported by an opened current source, downgrade it to `unverified` or attribute it as `company_claim`.

### 5. Build an evidence ledger

For every material claim, store source IDs and one evidence status:

- `confirmed`: supported by a primary or strong independent source.
- `company_claim`: stated by the company, founder, or its controlled channel but not independently verified.
- `analysis`: an inference from cited facts; phrase it as a judgment, not a fact.
- `unverified`: relevant but not adequately confirmed.

Also record every claim's `temporal_scope`, `materiality`, and `as_of` date. For every source record `authority`, `access_status`, and `freshness`. Use publication dates and access dates. Preserve contradictions and explain them briefly. Avoid sensitive personal data, rumors, and unsupported misconduct claims.

Never label a claim `confirmed` when it is supported only by the company, a search snippet, an inaccessible page, an aggregator, or an undated repost. Treat numerical calculations as `analysis`, show the inputs and formula, and cite the input sources.

### 6. Synthesize for an initial visit

Keep the visible narrative concise even when the search was detailed. Prioritize:

- one-sentence company positioning;
- customer problem and existing alternative;
- core product and technical route;
- clearest measurable differentiation;
- current engineering and commercialization stage;
- team and financing facts relevant to execution;
- competitive or substitute routes;
- 3–5 uncertainties that matter for the next decision.

Do not confuse customer contact with testing, testing with validation, a framework agreement with an order, first delivery with repeatability, or technical feasibility with a sellable product.

### 7. Select exactly three conversation topics

Make each topic specific to this company and suitable for a collaborative founder conversation. Across the three topics, normally cover:

1. Why this technical route wins for the customer's real constraint.
2. The path from present product stage to repeatable customer adoption.
3. The next 12 months: key milestone, organizational bottleneck, or use of financing.

For each topic provide: why it matters, a natural opening line, and what to listen for. Prefer topics that expose causal logic, not generic requests to “introduce the technology.”

### 8. Write exactly five critical questions

Tailor questions to the largest information gaps. Collectively test:

- customer problem and switching reason;
- measurable technical or product advantage;
- present engineering or validation stage;
- evidence from one representative customer journey;
- the next milestone and its main risk.

For each question include its purpose, a positive signal, and a red flag. Phrase questions conversationally and avoid an interrogation tone.

### 9. Run the reverse claim audit

Before rendering, inspect every visible sentence from conclusion back to source:

1. Can the cited page be opened now?
2. Does it state the claim, or is the wording an inference?
3. Is the source current enough for the claim's time scope?
4. Is a company statement being mistaken for independent confirmation?
5. Are contradictions, missing data, and unsuccessful searches visible?

Rewrite, downgrade, or remove any sentence that fails this audit. A shorter report with explicit unknowns is preferable to a complete-looking report with invented connective tissue.

### 10. Generate the HTML

Read [references/output-schema.md](references/output-schema.md). Create a UTF-8 JSON file matching the schema, then run:

```powershell
python scripts/render_brief.py --input <brief.json> --output <company>-拜访准备.html --max-research-age-days 7
```

The renderer rejects stale research by default, invalid dates, search-result URLs, unsupported evidence labels, company-only “confirmed” claims, inaccessible sources used as confirmation, critical claims without cross-checks, and any result that does not contain exactly 3 topics and 5 questions. Use `--allow-stale-research` only when deliberately re-rendering a historical report; never use it to present old research as current.

Open the generated HTML or inspect it in a browser/rendering tool when available. Verify:

- company identity and research date are visible;
- every material claim has the correct evidence badge and source link;
- all links work syntactically and no HTML is injected from source text;
- layout is readable on desktop, mobile, and print;
- there are exactly 3 topics and 5 questions;
- the evidence and freshness audit is visible and matches the ledger;
- no placeholder text remains.

## Output quality bar

- Prefer 8–15 useful sources across at least 4 source categories when public information permits; never pad the list.
- Prefer original or primary sources. Use aggregators as discovery aids and label paywalled or snippet-only evidence as weak.
- Put research date, information cutoff, evidence audit, and limitations at the top.
- Cross-check each critical confirmed claim with at least two opened current sources from different publishers; otherwise downgrade it.
- Treat absence of search results as “not found in this search,” never as proof that an event, customer, dispute, or risk does not exist.
- Make unknowns visible instead of filling gaps with inference.
- Keep the main briefing scannable in roughly 5–8 minutes; place source detail at the end.
- In the final response, link the HTML file and summarize the company in one sentence. Do not repeat the entire briefing in chat.

## Bundled resources

- [references/research-guide.md](references/research-guide.md): source hierarchy, query matrix, and synthesis rules.
- [references/output-schema.md](references/output-schema.md): versioned JSON contract and evidence/freshness fields.
- `scripts/render_brief.py`: enforces evidence and recency gates and creates a self-contained HTML report.
- `scripts/test_render_brief.py`: regression tests for hallucination and stale-information failure modes.
