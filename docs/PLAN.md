# Claude for Data Governance Teams: Plan

A starter kit for teams beginning a data governance program, modeled on the shape of Anthropic's [Claude for Financial Services](https://www.anthropic.com/news/claude-for-financial-services): one packaged solution made of (1) the model and tooling, (2) connectors into the systems of record, (3) ready-made workflows, and (4) implementation guidance.

## 0. Decisions (locked)

| Question | Decision |
|---|---|
| Audience | **Product pitch**: this repo is the demo and proof that a packaged "Claude for Data Governance" can be sold, not only an internal kit |
| Industry | **Insurance first** (claims data, NAIC / state DOI, NAIC Model Audit Rule, GLBA, GDPR/CCPA, SOX). Industry packs added later; core skills stay industry-neutral |
| Catalog | **Collibra first** (system of record for glossary, owners, assets) |
| Warehouse | Not decided. Assumed **Snowflake** because the seed skills use it. Confirm |
| Seed skills | Port the existing claims-DQ, glossary and steward-onboarding skills (done, see `skills/`) |

Pitch implications: the repo needs a 5-minute end-to-end demo on synthetic insurance claims data, a one-page value story with the metrics in section 7, and a security/trust page (section 5) that a buyer's CISO can read.

## 1. Goal and audience

Give a team that is *starting* governance (a few stewards, a CDO sponsor, no mature tooling) a working baseline in 90 days: agreed vocabulary, owned critical data, measured quality, and documented policy, with Claude doing the drafting and triage work that normally stalls programs.

Audience: Chief Data Officer, governance lead, data stewards, data owners, platform/data engineers, privacy and compliance partners.

## 2. Solution pillars (mirrors the financial services structure)

| Pillar | Financial services | Data governance equivalent |
|---|---|---|
| Core | Claude + Claude Code + Enterprise | Claude + Claude Code + Enterprise, with a governance system prompt and guardrails |
| Data integrations | FactSet, Snowflake, Databricks, Box... | MCP connectors to catalogs, warehouses, ticketing, docs (section 4) |
| Skills / workflows | Due diligence, memos, models | Governance skills (section 3) |
| Implementation | Partners, hands-on support | Playbooks, templates, 30/60/90 roadmap in this repo |
| Trust | Data not used for training, source links | Every output cites its source asset and is routed to a human approver |

## 3. Skills (the core deliverable)

Each skill is a folder with `SKILL.md`, an input/output template, and 2-3 worked examples.

| # | Skill | Input | Output |
|---|---|---|---|
| 1 | Business glossary term definer | Term + sample columns/docs | Definition, boundary, examples, owner, approval note |
| 2 | Critical data element (CDE) identifier | Catalog metadata + business processes | Ranked CDE candidates with rationale |
| 3 | Data quality rule writer | Table profile | Rules (completeness, validity, uniqueness, timeliness) in SQL/dbt/Great Expectations |
| 4 | DQ triage and scorecard narrator | Rule results | Prioritized issues, plain-English scorecard |
| 5 | Classification and sensitivity tagger | Column names, samples (masked) | PII/PHI/financial tags with confidence |
| 6 | Lineage explainer | Lineage graph / SQL | Impact analysis, upstream/downstream summary |
| 7 | Policy drafter and mapper | Regulation text + current practice | Policy draft, control mapping (GDPR, CCPA, HIPAA, SOX, BCBS 239) |
| 8 | Access request reviewer | Request + classification + role | Approve/deny recommendation with reasoning |
| 9 | Steward onboarding coach | Role | Role-specific checklist and first-week tasks |
| 10 | Exception and remediation manager | Failed rule | Root-cause hypothesis, remediation playbook, owner |
| 11 | Governance council briefer | Metrics | Monthly decision-ready summary |

Start with 1, 3, 4, 5 (highest value, lowest integration cost).

### Seed skills already ported to `skills/`

| Plan skill | Ported folder |
|---|---|
| 1 Glossary term definer | `define-business-term` |
| 3 DQ rule writer | `goviq-claims-dq-rule-writing` |
| 3 Profiling (supports rules) | `goviq-claims-dq-profiling`, `goviq-claims-intelligent-profile-analysis` |
| 4 DQ triage / scorecard narrator | `goviq-claims-dq-triage`, `goviq-claims-dq-scorecard-narration` |
| 9 Steward onboarding coach | `goviq-steward-onboarding-coach` |
| 10 Exception and remediation | `goviq-claims-dq-exception-management`, `goviq-claims-dq-remediation-playbook` |
| Documentation of rules/assets | `goviq-claims-dq-documentation` |

Gaps still to build: 2 (CDE identifier), 5 (sensitivity tagger), 6 (lineage), 7 (policy mapper), 8 (access review), 11 (council briefer).

Follow-ups on the ported set: (a) rename `goviq-*` to neutral names if the product is not GovIQ-branded, (b) separate the insurance-specific content from the industry-neutral method so other industries can reuse the core, (c) remove or generalize tool-specific references (e.g. DQLabs handoff) behind a connector note.

## 4. Connectors (via MCP)

Build order for the pitch: **Collibra** (catalog, first) + **Snowflake** (warehouse, assumed), then the rest.

- **Catalog (first): Collibra.** Read: communities, domains, assets, glossary terms, owners/stewards, workflows. Write (phase 4, approval-gated): propose terms and attribute updates as draft assets, never auto-approve. Confirm API vs. an existing MCP server before building.
- **Warehouses:** Snowflake (first), then BigQuery, Databricks (Unity Catalog), Redshift
- **Later catalogs:** DataHub, OpenMetadata, Alation, Atlan, Microsoft Purview
- **Work tracking:** Jira, ServiceNow, Notion/Confluence
- **Comms:** Slack/Teams for steward Q&A
- **Docs:** SharePoint/Drive for policies and standards

Rule: read-only first. Write access (tagging, ticket creation) only after the approval workflow is proven.

## 5. Guardrails (non-negotiable for a governance product)

1. Human-in-the-loop: Claude proposes, a named steward approves; nothing publishes to the catalog automatically.
2. Never send raw sensitive values to the model; profile and mask upstream, pass aggregates and patterns.
3. Every answer cites the source asset, rule, or document.
4. Audit log of prompts, outputs, approver, and timestamp.
5. Confidence + "I don't know" is an acceptable output.

## 6. Roadmap

**Phase 0, weeks 0-2: Foundation**
- Interview stakeholders; pick 1 domain (insurance: Claims) and 3-5 critical tables.
- Build the synthetic insurance claims dataset used by the pitch demo.
- Stand up Claude workspace, connect one warehouse and one catalog (read-only).
- Exit: scoped domain, access working, success metrics agreed.

**Phase 1, weeks 3-6: Vocabulary and ownership**
- Skills 1, 2, 9. Draft glossary for the domain, name owners and stewards.
- Exit: 20-30 approved terms, CDEs listed, RACI published.

**Phase 2, weeks 7-10: Quality and classification**
- Skills 3, 4, 5, 10. Profile, generate rules, run, produce first scorecard, tag sensitive columns.
- Exit: rules running on CDEs, scorecard reviewed by council, sensitivity tags approved.

**Phase 3, weeks 11-13: Policy and operating model**
- Skills 6, 7, 8, 11. Draft policies, access review flow, monthly council briefing.
- Exit: policies signed off, council cadence running, second domain nominated.

**Phase 4, after day 90: Scale**
- Add domains, write-back to catalog, CI checks, metric tracking.

## 7. Success metrics

- Time to draft + approve a glossary term (baseline vs. target: -50%)
- % of CDEs with owner, definition, and active DQ rule (target 80% in domain)
- DQ issues triaged within SLA
- % sensitive columns tagged and reviewed
- Steward hours saved per month (self-reported)
- Draft acceptance rate (edited vs. rejected), the key trust signal

## 8. Proposed repo layout

```
README.md              overview, quick start
docs/PLAN.md           this plan
docs/guardrails.md     security + human-in-the-loop standard
docs/roadmap.md        30/60/90 detail
skills/<skill-name>/   SKILL.md, templates, examples
connectors/            MCP setup notes per system
templates/             RACI, policy, glossary, council deck
examples/              sample domain end to end (synthetic data)
```

## 9. Risks

| Risk | Mitigation |
|---|---|
| Hallucinated definitions or rules | Grounding in catalog metadata, citations, steward approval |
| Sensitive data leakage | Mask upstream, read-only, aggregate profiles only |
| Skills ignored because governance lacks sponsorship | Phase 0 exit requires named executive sponsor |
| Tool sprawl | Start with one warehouse + one catalog |
| Over-promising vs. regulation | Position as drafting aid, not legal advice |

## 10. Open questions

1. Warehouse to pair with Collibra: Snowflake (assumed)?
2. Branding: keep GovIQ naming in skills or use a neutral product name?
3. Is the repo public on purpose? It is currently public, and the ported skills are now in it.
4. Which insurance line leads the demo (P&C claims is what the seed skills cover)? Life and health differ.
5. Insurance compliance mapping scope for the policy skill: NAIC Model Audit Rule, state DOI data-security laws (NAIC Insurance Data Security Model Law), GLBA, GDPR/CCPA, SOX. Confirm priority.

Resolved: audience (product pitch), industry (insurance first), catalog (Collibra), seed skills (ported).
