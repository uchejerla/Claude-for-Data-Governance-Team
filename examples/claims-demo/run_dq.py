"""Run rules.json against synthetic claims in in-memory SQLite and print a scorecard."""
import json
import pathlib
import sqlite3

from generate_claims import generate

HERE = pathlib.Path(__file__).parent


def run(rows, rules):
    if not rows:
        raise ValueError("no rows to check")
    for r in rules:  # rules may be pasted in from outside; only plain SELECTs run
        if not r["fail_sql"].lstrip().upper().startswith("SELECT"):
            raise ValueError(f"{r['id']}: fail_sql must start with SELECT")
    db = sqlite3.connect(":memory:")
    cols = list(rows[0])
    db.execute(f"CREATE TABLE claims ({', '.join(cols)})")
    db.executemany(f"INSERT INTO claims VALUES ({', '.join('?' * len(cols))})",
                   [tuple(r[c] for c in cols) for r in rows])
    total = len(rows)
    results = []
    for r in rules:
        failed = db.execute(r["fail_sql"]).fetchone()[0]
        score = 1 - failed / total
        results.append({**r, "failed": failed, "score": score, "pass": score >= r["threshold"]})
    return total, results


def scorecard(total, results):
    out = [f"# Claims DQ scorecard ({total} rows)", "",
           "| Rule | Dimension | Element | Failed | Score | Threshold | Status |",
           "|---|---|---|---|---|---|---|"]
    for r in results:
        out.append(f"| {r['id']} | {r['dimension']} | {r['element']} | {r['failed']} | "
                   f"{r['score']:.1%} | {r['threshold']:.0%} | {'PASS' if r['pass'] else 'FAIL'} |")
    passed = sum(r["pass"] for r in results)
    out += ["", f"{passed}/{len(results)} rules passing."]
    return "\n".join(out)


if __name__ == "__main__":
    rules = json.loads((HERE / "rules.json").read_text())
    print(scorecard(*run(generate(), rules)))
