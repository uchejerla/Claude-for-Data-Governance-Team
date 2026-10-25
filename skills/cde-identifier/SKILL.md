---
name: cde-identifier
description: >
  Identify and justify critical data element (CDE) candidates for a data domain. Use when a data steward or
  governance lead asks "which columns are critical", "what should we govern first", "pick our CDEs", or
  provides catalog metadata and wants a ranked, explained shortlist. Insurance-first (claims, reserves,
  payments, statutory reporting); the method is industry-neutral.
version: "0.1"
---

# CDE identifier

Turn catalog metadata into a ranked CDE shortlist a steward can confirm. The deterministic scoring lives in
`examples/cde-identifier/identify_cdes.py`; your job is to run it on good metadata, explain the result, and
never invent facts the metadata does not contain.

## Flow

1. **Get the metadata.** Ask for a catalog export (or the columns of one table) with, per column: regulatory
   reports it feeds, whether it affects reserves or payments, count of downstream assets, key or not, and
   sensitivity tags. If a field is unknown, leave it out of the JSON. Do not guess.
2. **Run the script** on the JSON and read the table.
3. **Explain each candidate in business terms**: one sentence on why it matters (e.g. "feeds Schedule P, so a
   wrong value reaches the statutory filing"). Use the "why" column; do not add reasons the table lacks.
4. **Handle `needs metadata`**: list exactly which facts are missing and who could supply them (catalog admin,
   report owner).
5. **Hand over for confirmation**: output a short table (column, decision, reason, suggested owner role,
   next step: define term, add DQ rule, tag sensitivity). A steward approves; you do not.

## Guardrails

- The score is a ranking aid, not a decision. Weights and cut-offs are demo values until the CDO agrees them.
- Sensitive-only columns need privacy controls; say so rather than forcing them into the CDE list.
- Never state a regulatory dependency that is not in the metadata. If unsure, mark it `NEEDS INPUT`.
- Next steps point to sibling skills: `define-business-term` for the glossary entry,
  `goviq-claims-dq-rule-writing` for rules.
