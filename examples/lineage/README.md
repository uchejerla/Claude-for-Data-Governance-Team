# Lineage explainer

Impact analysis over an asset-level lineage graph. Python 3 standard library only; the sample graph is synthetic.

```bash
python3 explain_lineage.py lineage_sample.json stg.claims          # what is affected if it changes
python3 explain_lineage.py lineage_sample.json rpt.schedule_p up   # where it comes from
python3 -m unittest -v
```

- Input is an edge list plus node details (`kind`, `owner`, `regulatory`). See `lineage_sample.json`.
- Shortest distance per asset; cycles are safe; unknown assets, edges or directions raise an error.
- Limit: no SQL parsing and no automatic harvesting. A catalog (Collibra later) would supply the edges.
