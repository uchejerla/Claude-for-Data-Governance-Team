# Claims DQ demo (no external tools)

Synthetic P&C claims with a known number of injected defects, seven DQ rules, and a scorecard. Pure Python 3 standard library (SQLite), so anyone can run it.

```bash
python3 run_dq.py          # print the scorecard
python3 -m unittest -v     # prove each rule finds exactly the injected defects
```

- `generate_claims.py`: 500 seeded rows plus `INJECTED`, the defect counts the tests assert against
- `rules.json`: rules as data (id, dimension, element, threshold, failing-row SQL)
- `run_dq.py`: runs the rules, prints the scorecard

## Skill outputs (generated from the scorecard)

- [output/triage_cards.md](output/triage_cards.md): triage cards for the five failing rules, from `goviq-claims-dq-triage`
- [output/scorecard_narration.md](output/scorecard_narration.md): executive and operational narrative, from `goviq-claims-dq-scorecard-narration`

Unknowns (prior period, dollar impact, source system) are marked `[NEEDS INPUT]`, not invented.

## Sensitivity tagger

```bash
python3 tag_sensitivity.py                      # tags a sample insurance schema
python3 tag_sensitivity.py claimant_ssn state   # or your own column names
```

Tags PII, PHI, GOV_ID and FINANCIAL_ACCOUNT from column names only. It is a first pass for a steward to review, not a classifier. The demo `claims` table has no sensitive columns, so the sample schema is used to show it working.

## Writing rules with Claude

`goviq-claims-dq-rule-writing` produces a text report (pseudo-SQL logic, a threshold in words, severity, and a "Sample SQL" block), not `rules.json` entries. To use a Claude-written rule here, adapt its Sample SQL into a `fail_sql` that returns a count of failing rows, and give it an `id`, `dimension`, `element` and numeric `threshold`. Only run rules you have read: `fail_sql` is executed as written.
