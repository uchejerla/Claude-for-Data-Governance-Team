# Policy mapper

Maps regulatory requirement themes to data governance controls, shows which are covered, partial or open, and ranks the missing controls by how many requirements each one blocks. Python 3 standard library only.

```bash
python3 map_policy.py --have C-01,C-02,C-04                      # all sources
python3 map_policy.py --have C-01 --sources NAIC-668,GDPR       # filter
python3 -m unittest -v
```

- `requirements.json`: 11 controls and 12 requirement themes across NAIC #668, GDPR, CCPA, NAIC #205 and SOX. Each control names the asset in this repo that supports it (`kit`), or `null` if not built yet; a test checks those paths exist.
- Unknown control ids or sources raise an error, so a typo cannot silently show as a gap.

## Read this before using it

The requirements are **plain-language themes written by Claude, not legal text, and not legal advice**. Applicability varies (state adoption of #668, premium thresholds for #205, EU data in scope for GDPR, CCPA insurance exemptions). Compliance or counsel must confirm every row before it goes into a policy or a customer-facing document. The `kit` column shows which controls this repo can already evidence and which are gaps in the product itself.

To add an industry or regulation: add a source and requirement rows to `requirements.json`; no code change.
