"""Run every tool in the kit on synthetic claims data and print one report (about 5 minutes to read).

Live from the run: DQ scorecard, sensitivity tags, CDE ranking and rule coverage, lineage impact, access reviews,
policy coverage, glossary validation, DQ and CDE figures in the brief. Sample inputs: the catalog metadata,
lineage graph, access requests, and the brief's other figures (terms, access counts, issues, prior period).
Usage: python3 run_demo.py
"""
import copy
import hashlib
import json
import pathlib
import sys
import tempfile

EX = pathlib.Path(__file__).resolve().parents[1]
for d in EX.iterdir():
    if d.is_dir() and d.name != "end-to-end":
        sys.path.insert(0, str(d))

import map_policy  # noqa: E402
from audit import log_event, verify  # noqa: E402
from explain_lineage import impact  # noqa: E402
from mask import assert_no_leaks, mask_rows  # noqa: E402
from generate_claims import generate  # noqa: E402
from identify_cdes import rank  # noqa: E402
from make_brief import brief  # noqa: E402
from review_access import review  # noqa: E402
from run_dq import run, scorecard  # noqa: E402
from tag_sensitivity import SAMPLE, tag_columns  # noqa: E402
from validate_term import validate  # noqa: E402


def load(rel):
    return json.loads((EX / rel).read_text())


def build():
    out = ["# End-to-end demo: Claude for Data Governance (synthetic insurance claims)", ""]

    rules = load("claims-demo/rules.json")
    total, results = run(generate(), rules)
    out += ["## 1. Data quality: are the claims trustworthy?", "", scorecard(total, results).split("\n", 2)[2], ""]

    out += ["## 2. Sensitivity: which columns need protecting?", "", "| Column | Tags |", "|---|---|"]
    out += [f"| {c} | {', '.join(t)} |" for c, t in tag_columns(SAMPLE).items() if t]
    out.append("")

    candidates = [r for r in rank(load("cde-identifier/catalog_sample.json")) if r["decision"] == "CDE candidate"]
    ruled = {r["element"] for r in rules}
    covered = [c for c in candidates if c["column"] in ruled]
    out += ["## 3. Critical data elements: what do we govern first?", "", "| CDE candidate | Score | DQ rule |", "|---|---|---|"]
    out += [f"| {c['column']} | {c['score']} | {'yes' if c in covered else 'none yet'} |" for c in candidates]
    out.append("")

    reached = impact(load("lineage/lineage_sample.json"), "stg.claims")
    regs = [r["asset"] for r in reached if r.get("regulatory")]
    out += ["## 4. Lineage: what breaks if the staging claims table is wrong?", "",
            f"{len(reached)} downstream assets; regulatory reports affected: {', '.join(regs)}.", ""]

    out += ["## 5. Access: who may see what?", ""]
    out += [f"- {r['requester']} -> {r['dataset']}: **{r['decision']}**" + (f" ({r['reasons'][0]})" if r["reasons"] else "")
            for r in map(review, load("access-review/requests_sample.json"))]
    out.append("")

    have = [c for c, v in map_policy.DATA["controls"].items() if v["kit"]]
    rows = map_policy.coverage(have)
    counts = {s: sum(1 for r in rows if r["status"] == s) for s in ("covered", "partial", "gap")}
    top = ", ".join(f"{c} ({map_policy.DATA['controls'][c]['name']})" for c, _ in map_policy.priorities(rows)[:3])
    out += ["## 6. Policy: what does this kit already evidence?", "",
            f"Controls the kit evidences today: {', '.join(have)}. Of {len(rows)} requirement themes: "
            f"{counts['covered']} covered, {counts['partial']} partial, {counts['gap']} gap. Build next: {top}.",
            f"_{map_policy.DATA['_notice']}_", ""]

    good = validate((EX / "glossary-validator/good-open-claim.md").read_text())
    bad = validate((EX / "glossary-validator/bad-active-customer.md").read_text())
    out += ["## 7. Glossary: is a proposed term fit for review?", "",
            f"- {good['term']}: **{good['verdict']}**",
            f"- {bad['term']}: **{bad['verdict']}** ({len(bad['findings'])} findings; its own file claimed '{bad['claimed']}')", ""]

    metrics = copy.deepcopy(load("council-brief/metrics_sample.json"))
    metrics["current"].update(
        dq_overall=round(100 * sum(r["score"] for r in results) / len(results), 1),
        rules_passing=sum(r["pass"] for r in results), rules_total=len(results),
        cde_total=len(candidates), cde_with_dq_rule=len(covered))
    out += ["## 8. Council brief (DQ and CDE figures live, the rest sample)", "", brief(metrics).split("\n", 2)[2].replace("## ", "### ")]
    out += ["", "## 9. Safeguards: masking before Claude, audit trail after", ""]
    sample = {"claim_id": "CLM1", "claimant_name": "Jane Roe", "claimant_ssn": "123-45-6789",
              "adjuster_notes": "Call claimant on 555-123-4567", "claim_amount": 1200.5}
    (masked,), report = mask_rows([sample], "demo-key-not-secret")
    assert_no_leaks([masked])
    out += ["Masked record (demo key, never use a demo key for real data):", "",
            *[f"- {c}: {v}" for c, v in masked.items()], "",
            f"Report counts only: {report}. Leak gate: passed.", ""]
    denied = [r for r in map(review, load("access-review/requests_sample.json")) if r["decision"] == "deny"][0]
    with tempfile.TemporaryDirectory() as d:
        log = pathlib.Path(d) / "audit.jsonl"
        rec = log_event(log, "recommendation", now="2026-10-25T10:00:00+00:00", requester=denied["requester"],
                        skill="access-request-reviewer", skill_version="0.1", input_ref="requests_sample.json",
                        output_sha256=hashlib.sha256(json.dumps(denied, sort_keys=True).encode()).hexdigest(),
                        recommendation=denied["decision"])
        log_event(log, "decision", now="2026-10-25T11:00:00+00:00", ref=rec["seq"],
                  approver="R. Gomez (example name)", decision="rejected")
        intact = verify(log)
        log.write_text(log.read_text().replace('"deny"', '"recommend-approve"'))
        tampered = verify(log)
    out += [f"Audit log: 2 records, chain check **{'intact' if not intact else 'broken'}**. "
            f"After editing the recommendation by hand: **{'intact' if not tampered else 'tampering detected'}** "
            f"({tampered[0] if tampered else 'no problems'})."]
    return "\n".join(out)


if __name__ == "__main__":
    print(build())
