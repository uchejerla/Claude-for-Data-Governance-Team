# CDE identifier

Ranks columns as critical data element (CDE) candidates from catalog metadata. Python 3 standard library only. The sample metadata is synthetic and stands in for a catalog export (Collibra later).

```bash
python3 identify_cdes.py catalog_sample.json
python3 -m unittest -v
```

## Scoring (demo values, agree with the CDO before use)

| Criterion | Points |
|---|---|
| Feeds a regulatory report | +3 |
| Affects reserves or payments | +3 |
| Used by 10+ downstream assets (3 to 9: +1) | +2 |
| Join key or identifier | +2 |
| Special-category data: GOV_ID, PHI, FINANCIAL_ACCOUNT (other personal data: +1) | +3 |

Cut-offs: 7 or more is a CDE candidate, 3 to 6 is steward review, below 3 is not a CDE. A column with missing metadata that scores low is `needs metadata`, never "not a CDE". The missing fields are listed.

Design notes:
- Output always shows the reasons, so a steward can argue with the points, not a black box.
- The `sensitivity` field can come from `examples/claims-demo/tag_sensitivity.py`.
- Sensitive-only columns (the SSN) land in steward review, not candidate: they need privacy controls, which is a different decision from being critical to reporting. Change the points if your program treats them as CDEs.
- It ranks and explains; a steward confirms. Nothing here approves a CDE.
