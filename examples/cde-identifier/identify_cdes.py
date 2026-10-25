"""Rank columns as critical data element (CDE) candidates from catalog metadata.

Scoring is a transparent point scheme (see WEIGHTS); the weights and cut-offs are demo values to be agreed
with the CDO. A missing metadata field scores 0 and is listed under `unknown` so it can be filled in, not guessed.
Usage: python3 identify_cdes.py catalog.json
"""
import json
import pathlib
import sys

CANDIDATE, REVIEW = 7, 3  # score >= CANDIDATE: CDE candidate; >= REVIEW: steward review; else not a CDE
SPECIAL = {"GOV_ID", "PHI", "FINANCIAL_ACCOUNT"}


def score(col):
    pts, why, unknown = 0, [], []
    for key in ("regulatory_reports", "financial_impact", "downstream_assets", "is_key", "sensitivity"):
        if key not in col:
            unknown.append(key)
    regs = col.get("regulatory_reports") or []
    if regs:
        pts += 3
        why.append(f"feeds regulatory reporting ({', '.join(regs)}) +3")
    if col.get("financial_impact"):
        pts += 3
        why.append("affects reserves or payments +3")
    n = col.get("downstream_assets") or 0
    if n >= 10:
        pts += 2
        why.append(f"used by {n} downstream assets +2")
    elif n >= 3:
        pts += 1
        why.append(f"used by {n} downstream assets +1")
    if col.get("is_key"):
        pts += 2
        why.append("join key or identifier +2")
    sens = set(col.get("sensitivity") or [])
    if sens & SPECIAL:
        pts += 3
        why.append(f"special-category data ({', '.join(sorted(sens & SPECIAL))}) +3")
    elif sens:
        pts += 1
        why.append(f"personal data ({', '.join(sorted(sens))}) +1")
    decision = ("CDE candidate" if pts >= CANDIDATE else "steward review" if pts >= REVIEW
                else "needs metadata" if unknown else "not a CDE")  # don't call a column non-critical on missing facts
    return {"column": col["column"], "score": pts, "decision": decision, "why": why, "unknown": unknown}


def rank(columns):
    return sorted((score(c) for c in columns), key=lambda r: (-r["score"], r["column"]))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    print("| Column | Score | Decision | Why | Unknown |\n|---|---|---|---|---|")
    for r in rank(json.loads(pathlib.Path(sys.argv[1]).read_text())):
        print(f"| {r['column']} | {r['score']} | {r['decision']} | {'; '.join(r['why']) or '-'} | {', '.join(r['unknown']) or '-'} |")
    print(f"\nCandidates need steward confirmation. Cut-offs: >={CANDIDATE} candidate, >={REVIEW} review.")
