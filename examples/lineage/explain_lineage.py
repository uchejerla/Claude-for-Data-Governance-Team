"""Impact analysis over an asset-level lineage graph given as an edge list.

shortcut: edge list in, so no SQL parsing and no column-level lineage unless nodes are named per column;
upgrade to a catalog or SQL-parser feed when lineage must be harvested automatically.
Usage: python3 explain_lineage.py graph.json ASSET [up|down]    (default: down)
"""
import json
import pathlib
import sys
from collections import deque


def walk(graph, start, direction="down"):
    """Breadth-first walk; returns {asset: shortest distance} excluding start. Safe on cycles."""
    nodes = graph["nodes"]
    if start not in nodes:
        raise ValueError(f"unknown asset: {start}")
    if direction not in ("up", "down"):
        raise ValueError("direction must be 'up' or 'down'")
    nxt = {}
    for a, b in graph["edges"]:
        if a not in nodes or b not in nodes:
            raise ValueError(f"edge references unknown asset: {a} -> {b}")
        src, dst = (a, b) if direction == "down" else (b, a)
        nxt.setdefault(src, []).append(dst)
    seen, queue = {start: 0}, deque([start])
    while queue:
        n = queue.popleft()
        for m in nxt.get(n, []):
            if m not in seen:
                seen[m] = seen[n] + 1
                queue.append(m)
    del seen[start]
    return seen


def impact(graph, asset, direction="down"):
    reached = walk(graph, asset, direction)
    rows = [{"asset": a, "distance": d, **graph["nodes"][a]} for a, d in reached.items()]
    return sorted(rows, key=lambda r: (r["distance"], r["asset"]))


def explain(graph, asset, direction="down"):
    rows = impact(graph, asset, direction)
    word = "downstream (affected if it changes)" if direction == "down" else "upstream (feeds it)"
    out = [f"{asset}: {len(rows)} assets {word}", "", "| Distance | Asset | Kind | Owner | Regulatory |", "|---|---|---|---|---|"]
    out += [f"| {r['distance']} | {r['asset']} | {r['kind']} | {r.get('owner', 'OPEN')} | {'yes' if r.get('regulatory') else '-'} |" for r in rows]
    reg = [r["asset"] for r in rows if r.get("regulatory")]
    if direction == "down":
        out.append(f"\nRegulatory reports affected: {', '.join(reg) if reg else 'none'}")
    return "\n".join(out)


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    print(explain(json.loads(pathlib.Path(sys.argv[1]).read_text()), sys.argv[2], *sys.argv[3:]))
