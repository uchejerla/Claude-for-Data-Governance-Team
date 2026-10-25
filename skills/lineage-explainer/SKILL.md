---
name: lineage-explainer
description: >
  Explain data lineage and change impact in plain language. Use when someone asks "what breaks if this table
  changes", "where does this report's data come from", "which regulatory reports use this column", or provides
  a lineage graph or catalog lineage export. Insurance-first (claims to Schedule P, state reports).
version: "0.1"
---

# Lineage explainer

Graph walking is deterministic: `examples/lineage/explain_lineage.py` over an asset edge list
(`lineage_sample.json` shows the format). You supply the translation into business impact.

## Flow

1. **Get the graph.** An edge list of `[source, target]` pairs plus node details (kind, owner, `regulatory: true`
   for statutory or regulator-facing reports). If the user has none, say lineage must come from the catalog and
   offer the sample format; never infer edges from table names.
2. **Pick direction.** Downstream for "what is affected", upstream for "where does it come from".
3. **Run** `explain_lineage.py graph.json ASSET [up|down]`.
4. **Explain in business terms**: lead with regulatory reports affected, then dashboards, then owners to notify,
   nearest first (distance 1 is a direct dependency).
5. **Suggest next steps**: notify named owners, add a DQ rule at the earliest shared node, or link to the
   `policy-mapper` control C-08 (lineage for reported figures).

## Guardrails

- Only report assets and owners present in the graph. A missing owner is `OPEN`, not a guess.
- Lineage is only as complete as its input. Say "no downstream assets in this graph", not "nothing depends on it".
- Distances are shortest paths, not a count of every route.
