"""Check a glossary term proposal (skills/define-business-term template) against the rubric's mechanical items.

Judgement items (synonym circularity, atomic, plain language, real examples) are not checked; a human still reviews.
Usage: python3 validate_term.py term.md [more.md ...]   (exit 1 if any file has a blocker)
"""
import pathlib
import re
import sys

VAGUE = r"\b(active|current|recent|complete|material|valid)\b"
IMPLEMENTATION = r"\b(table|column|schema|database|sql|select)\b|\b[a-z0-9]+_[a-z0-9_]+\b"


def blank(v):
    v = (v or "").strip()
    return not v or (v.startswith("<") and v.endswith(">"))


def unnamed(v):
    return blank(v) or v.strip().upper() == "OPEN"


def parse(text):
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        raise ValueError("missing front matter")
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = re.sub(r"\s+#.*$", "", v.strip()).strip().strip('"')
    body = re.sub(r"<!--.*?-->", "", m.group(2), flags=re.S)
    sections = {n.strip().lower(): c.strip()
                for n, c in re.findall(r"^## (.+?)\n(.*?)(?=^## |\Z)", body, re.S | re.M)}
    return meta, sections


def field(text, label):
    m = re.search(rf"\*\*{re.escape(label)}:\*\*(.*?)(?=\n[-\s]*\*\*|\Z)", text, re.S)
    return m.group(1).strip() if m else ""


def rows(text):
    out = [[c.strip() for c in ln.strip().strip("|").split("|")]
           for ln in text.splitlines()
           if ln.startswith("|") and not re.match(r"\|[\s\-|]+\|?$", ln)]
    return out[1:]  # drop header row


def validate(text):
    meta, sec = parse(text)
    term = "" if blank(meta.get("term")) else meta["term"]
    definition = sec.get("definition", "")
    boundary, flags = sec.get("boundary", ""), sec.get("flags", "")
    dup = sec.get("duplicate and homonym check", "")
    evidence = sec.get("source evidence", "")
    body = re.compile(rf"^\s*(the |an? )?{re.escape(term)}\s+(is|are)\b", re.I).sub("", definition) if term else definition
    ex = rows(sec.get("examples", ""))
    count = lambda kind: sum(1 for r in ex if len(r) > 1 and r[0].lower() == kind and r[1])

    checks = [  # (id, severity, ok, message when failed)
        ("B0", "blocker", not blank(definition), "Definition is empty"),
        ("B1", "blocker", not (unnamed(evidence) and definition.strip().upper() != "OPEN"),
         "No source evidence and the definition is not marked OPEN"),
        ("B2", "blocker", not (term and re.search(rf"\b{re.escape(term)}\b", body, re.I)),
         f"Definition uses the term '{term}' itself"),
        ("B3", "blocker", not unnamed(meta.get("scope")), "Scope is not stated"),
        ("B4", "blocker", not (re.search(VAGUE, definition, re.I) and blank(field(boundary, "Threshold"))),
         "Definition uses active/current/recent/complete/material/valid but no Threshold is given (OPEN is allowed)"),
        ("B5", "blocker", not all(unnamed(meta.get(k)) for k in ("steward", "sme", "approver")),
         "No steward, SME or approver is named"),
        ("B6", "blocker", not (blank(meta.get("duplicate_check")) or blank(field(dup, "Surface searched"))),
         "Duplicate check not recorded (where searched and what was found)"),
        ("B7", "blocker", not re.search(IMPLEMENTATION, definition, re.I),
         "Definition names a table, column, schema, SQL or similar"),
        ("M1", "major", not (blank(field(boundary, "In scope")) or blank(field(boundary, "Out of scope"))),
         "Boundary needs both In scope and Out of scope"),
        ("M2", "major", count("positive") >= 2 and count("negative") >= 1,
         "Needs at least 2 positive and 1 negative example"),
        ("M3", "major", sum(1 for r in rows(sec.get("contrasting terms", "")) if len(r) > 1 and r[0] and r[1]) >= 2,
         "Needs 2 contrasting terms with the difference stated"),
        ("M5", "major", len([s for s in re.split(r"(?<=[.!?])\s+", definition) if s.strip()]) <= 3,
         "Definition is longer than 3 sentences"),
        ("M7", "major", not (blank(meta.get("sensitivity")) or blank(field(flags, "Sensitivity"))),
         "Sensitivity not assessed"),
        ("N5", "minor", not term.endswith("."), "Term label ends with a period"),
    ]
    findings = [(i, sev, msg) for i, sev, ok, msg in checks if not ok]
    blockers = sum(1 for f in findings if f[1] == "blocker")
    majors = sum(1 for f in findings if f[1] == "major")
    verdict = "not-publishable" if blockers else "ready-for-review" if not majors else "needs-work"
    return {"term": term or "(unnamed)", "verdict": verdict, "claimed": meta.get("verdict", ""),
            "findings": findings, "passed": len(checks) - len(findings), "total": len(checks)}


def report(path, r):
    out = [f"{path}: {r['term']}", f"  Verdict: {r['verdict']}  ({r['passed']}/{r['total']} mechanical checks passed)"]
    if r["claimed"] and r["claimed"] != r["verdict"]:
        out.append(f"  MISMATCH: file claims verdict '{r['claimed']}'")
    out += [f"  FAIL {i} ({sev}): {msg}" for i, sev, msg in r["findings"]]
    return "\n".join(out)


if __name__ == "__main__":
    results = [(p, validate(pathlib.Path(p).read_text())) for p in sys.argv[1:]]
    print("\n\n".join(report(p, r) for p, r in results) or __doc__)
    sys.exit(any(r["verdict"] == "not-publishable" for _, r in results))
