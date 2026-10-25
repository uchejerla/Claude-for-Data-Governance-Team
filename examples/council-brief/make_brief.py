"""Build the factual core of a monthly governance council brief from a metrics file.

Computes numbers, changes versus the prior period, and flags. It writes no narrative and invents nothing:
decisions come only from the input. Claude adds the story around these facts (see skills/council-briefer).
Usage: python3 make_brief.py metrics.json
"""
import json
import pathlib
import sys


def pct(part, whole):
    return 100 * part / whole if whole else None  # unrounded: rounding before subtracting gives off-by-0.1 changes


def show(v):
    return "n/a" if v is None else f"{v:.1f}" if isinstance(v, float) else str(v)


def values(m):
    return {
        "DQ overall score (%)": m["dq_overall"],
        "DQ rules passing": m["rules_passing"],
        "CDEs with an owner (%)": pct(m["cde_with_owner"], m["cde_total"]),
        "CDEs with an active DQ rule (%)": pct(m["cde_with_dq_rule"], m["cde_total"]),
        "Glossary terms approved": m["terms_approved"],
        "Glossary terms in review": m["terms_in_review"],
        "Access requests pending": m["access_pending"],
    }


def change(cur, prior):
    if cur is None or prior is None:
        return "n/a"
    d = round(cur - prior, 1)
    return f"{d:+g}"


def flags(metrics):
    cur, out = metrics["current"], []
    if cur["rules_passing"] < cur["rules_total"]:
        out.append(f"{cur['rules_total'] - cur['rules_passing']} of {cur['rules_total']} DQ rules are below target")
    sla = metrics["issue_sla_days"]
    for i in metrics["open_issues"]:
        if i["severity"] not in sla:
            raise ValueError(f"{i['id']}: no SLA for severity '{i['severity']}'")
        if i["age_days"] > sla[i["severity"]]:
            out.append(f"{i['id']} {i['title']} ({i['severity']}) is {i['age_days']} days old, SLA is {sla[i['severity']]}")
    for label, v in values(cur).items():
        if label.startswith("CDEs") and v is not None and v < metrics["cde_coverage_target"]:
            out.append(f"{label} is {v:.1f}%, target is {metrics['cde_coverage_target']}%")
    return out


def brief(metrics):
    cur, prior = values(metrics["current"]), values(metrics.get("prior") or {**metrics["current"], **{k: None for k in metrics["current"]}})
    out = [f"# Governance council brief: {metrics['period']}", "", "## Numbers", "",
           "| Metric | Now | Prior | Change |", "|---|---|---|---|"]
    out += [f"| {k} | {show(v)} | {show(prior[k])} | {change(v, prior[k])} |" for k, v in cur.items()]
    f = flags(metrics)
    out += ["", "## Needs attention", ""] + ([f"- {x}" for x in f] or ["- Nothing flagged"])
    out += ["", "## Decisions needed", ""] + ([f"{n}. {d}" for n, d in enumerate(metrics["decisions"], 1)] or ["None this month"])
    out += ["", "_Facts computed from the supplied metrics. Narrative is added separately._"]
    return "\n".join(out)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    print(brief(json.loads(pathlib.Path(sys.argv[1]).read_text())))
