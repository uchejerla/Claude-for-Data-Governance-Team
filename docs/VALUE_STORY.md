# Claude for Data Governance Teams: value story

**For:** Chief Data Officers and governance leads at insurers who have a mandate and a small team, but no working governance baseline yet.

## The problem

Governance programs stall on the same work: writing definitions nobody agrees on, finding out which data matters, checking quality by hand, answering "who can see this" one email at a time, and turning it all into a monthly update. A team of a few stewards cannot keep pace, so the program produces policy documents instead of controlled data.

## What this kit gives a starting team

A working baseline for one domain (Claims first), where Claude does the drafting, explaining and triage and a named human approves every result.

| Governance job | What the kit does | Human decides |
|---|---|---|
| Vocabulary | Drafts glossary terms and checks them against a rubric before review | Approver signs off the term |
| What matters most | Ranks critical data elements with the reasons shown | Steward confirms the list |
| Quality | Writes and runs rules, produces a scorecard, triage cards and a narrative | Steward sets severity and owners |
| Sensitive data | Flags likely PII, PHI and ID columns from column names | Steward confirms before any tag is applied |
| Impact | Shows which reports break if a table is wrong, regulatory reports first | Owners are notified by the team |
| Access | Recommends approve, pending or deny with reasons against policy | Data owner decides |
| Policy | Maps regulation themes to controls and ranks what to build next | Compliance confirms the themes |
| Reporting | Computes the monthly council brief numbers and flags | Lead writes the decisions |

## Why a buyer can trust it

- Claude proposes; a named person approves. Nothing publishes on its own.
- Every number is computed by tested code, not written by the model. Unknowns are marked `NEEDS INPUT`, never guessed.
- Each tool states its limits in its README, and the policy mapper says plainly that its regulation themes are not legal text.
- [docs/guardrails.md](guardrails.md) lists every guardrail with its status (enforced by tested code, instructed in a skill, or not built yet) and answers the questions a security team will ask.

## Proof you can run today

`python3 examples/end-to-end/run_demo.py` runs the whole chain on synthetic claims data in seconds: 7 quality rules finding 42 planted defects exactly, 3 critical data elements, the 3 regulatory reports affected by a staging table, 6 access decisions with reasons, and a council brief. Each piece has automated tests (53 tests across the example folders).

## What is not proven yet

- It has not run against real data or a real catalog. Everything above uses synthetic data. The Collibra connector is not built.
- No time-saved or accuracy figures exist yet, and none are claimed here. A pilot should measure: time from draft to approved term, share of CDEs with an owner and an active rule, draft acceptance rate, and steward hours saved.
- Weights, thresholds, the access policy and the regulation themes are demo values. Each needs the customer's own numbers and a Compliance review.

## Proposed pilot

One domain (Claims), 3 to 5 critical tables, 13 weeks (see `docs/PLAN.md`): glossary and ownership first, then quality and classification, then policy and the council cadence. Exit criteria are the measures above, taken against the customer's baseline.
