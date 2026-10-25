# End-to-end demo

One command runs every tool in the kit on synthetic insurance claims data and prints a single report.

```bash
python3 run_demo.py
python3 -m unittest -v
```

Sections: data quality, sensitivity, critical data elements, lineage impact, access reviews, policy coverage, glossary validation, council brief.

What is live and what is sample is stated in the script header and in section 8 of the report. The claims data, DQ results, sensitivity tags, CDE ranking, lineage impact, access decisions, policy coverage and glossary verdicts are computed on each run. The catalog metadata, lineage graph, access requests, and the brief's non-DQ figures (terms, access counts, open issues, prior period) are sample files.
