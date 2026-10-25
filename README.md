# Claude for Data Governance Teams

A starting point for teams implementing data governance with Claude: governance skills, system connectors, guardrails, and a 90-day roadmap.

- **Skills:** glossary, critical data elements, data quality rules and scorecards, classification, lineage, policy, access review, steward onboarding
- **Connectors:** warehouses, catalogs, ticketing, docs (read-only first)
- **Guardrails:** human approval, no raw sensitive data to the model, cited sources, audit trail

- Value story (for buyers): [docs/VALUE_STORY.md](docs/VALUE_STORY.md)
- Run the demo: `python3 examples/end-to-end/run_demo.py` (Python 3, no installs)
- Plan: [docs/PLAN.md](docs/PLAN.md)

Status: 11 skills with tested tools on synthetic insurance claims data. Not yet run on real data. The Collibra connector is not built, and the guardrails above are design commitments; `docs/guardrails.md` is still to be written.
