"""Map regulatory requirement themes to data governance controls and show coverage gaps.

Usage: python3 map_policy.py --have C-01,C-02 [--sources NAIC-668,GDPR]
The requirement texts are plain-language themes, not legal text; Compliance must confirm them.
"""
import argparse
import json
import pathlib

DATA = json.loads((pathlib.Path(__file__).parent / "requirements.json").read_text())


def coverage(have, sources=None):
    have, sources = set(have), set(sources or DATA["sources"])
    if have - set(DATA["controls"]):
        raise ValueError(f"unknown controls: {sorted(have - set(DATA['controls']))}")
    if sources - set(DATA["sources"]):
        raise ValueError(f"unknown sources: {sorted(sources - set(DATA['sources']))}")
    rows = []
    for r in DATA["requirements"]:
        if r["source"] not in sources:
            continue
        missing = [c for c in r["controls"] if c not in have]
        status = "covered" if not missing else "gap" if len(missing) == len(r["controls"]) else "partial"
        rows.append({**r, "status": status, "missing": missing})
    return rows


def priorities(rows):
    """Missing controls ranked by how many requirements each one blocks (ties by id)."""
    count = {}
    for r in rows:
        for c in r["missing"]:
            count[c] = count.get(c, 0) + 1
    return sorted(count.items(), key=lambda kv: (-kv[1], kv[0]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--have", default="", help="comma-separated implemented control ids")
    ap.add_argument("--sources", help="comma-separated sources (default: all)")
    a = ap.parse_args()
    rows = coverage([c for c in a.have.split(",") if c], a.sources.split(",") if a.sources else None)
    print("| Req | Source | Requirement | Status | Missing controls |\n|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['id']} | {r['source']} | {r['text']} | {r['status']} | {', '.join(r['missing']) or '-'} |")
    print("\nBuild next (controls blocking the most requirements):")
    for c, n in priorities(rows):
        ctl = DATA["controls"][c]
        print(f"- {c} {ctl['name']}: blocks {n}" + (f" (kit: {ctl['kit']})" if ctl["kit"] else ""))
    print(f"\n{DATA['_notice']}")
