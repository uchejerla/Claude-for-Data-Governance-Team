# Claims DQ demo (no external tools)

Synthetic P&C claims with a known number of injected defects, six DQ rules, and a scorecard. Pure Python 3 standard library (SQLite), so anyone can run it.

```bash
python3 run_dq.py          # print the scorecard
python3 -m unittest -v     # prove each rule finds exactly the injected defects
```

- `generate_claims.py`: 500 seeded rows plus `INJECTED`, the defect counts the tests assert against
- `rules.json`: rules as data (id, dimension, element, threshold, failing-row SQL)
- `run_dq.py`: runs the rules, prints the scorecard

How it fits the pitch: the scorecard is the input to the `goviq-claims-dq-triage` and `goviq-claims-dq-scorecard-narration` skills. Paste it into Claude with those skills to get the prioritized issues and the executive narrative. Rule format maps 1:1 to `goviq-claims-dq-rule-writing` output, so Claude-written rules can be dropped into `rules.json`.
