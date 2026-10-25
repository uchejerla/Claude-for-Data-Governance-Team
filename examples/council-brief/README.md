# Council brief

Builds the factual core of a monthly governance council brief from a metrics file: numbers with change versus the prior period, flags (rules below target, issues past SLA, CDE coverage below target) and the decisions requested. Python 3 standard library only; the sample metrics are synthetic.

```bash
python3 make_brief.py metrics_sample.json
python3 -m unittest -v
```

- Writes no narrative and invents nothing. Decisions appear only if the input lists them. Claude adds the story around these facts (`skills/council-briefer`).
- Changes are computed from unrounded values, so percent changes are not off by 0.1; a test covers it.
- Missing prior period shows `n/a`. Zero CDEs does not crash. An issue with an unknown severity raises an error instead of being silently skipped.
