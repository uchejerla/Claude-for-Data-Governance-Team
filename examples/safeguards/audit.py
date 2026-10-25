"""Append-only, hash-chained audit log for Claude-assisted governance decisions (JSON lines).

Two record kinds: a `recommendation` (what Claude/a tool proposed) and a later `decision` by a named human that
points back at it by `ref`. Each record carries the hash of the one before, so edits, deletions and reordering
are detectable with verify(). Fields are checked so raw sensitive data cannot be written into the log.

shortcut: single writer, no file locking, and cutting records off the end is only detectable against a head()
you stored elsewhere; upgrade to an append-only database or write-once store for multi-writer or regulated use.
"""
import datetime
import hashlib
import json
import pathlib
import re

from mask import find_leaks

ZERO = "0" * 64
REQUIRED = {
    "recommendation": ("requester", "skill", "skill_version", "input_ref", "output_sha256", "recommendation"),
    "decision": ("ref", "approver", "decision"),
}
DECISIONS = {"approved", "rejected", "deferred"}
NOT_HUMAN = {"claude", "ai", "assistant", "system", "bot", "llm"}


def _digest(rec):
    body = {k: v for k, v in rec.items() if k != "hash"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read(path):
    p = pathlib.Path(path)
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()] if p.exists() else []


def log_event(path, kind, now=None, **fields):
    if kind not in REQUIRED:
        raise ValueError(f"kind must be one of {sorted(REQUIRED)}")
    missing = [k for k in REQUIRED[kind] if str(fields.get(k, "")).strip() == ""]
    extra = set(fields) - set(REQUIRED[kind]) - {"note"}
    if missing or extra:
        raise ValueError(f"missing fields {missing}, unexpected fields {sorted(extra)}")
    if "output_sha256" in fields and not re.fullmatch(r"[0-9a-f]{64}", str(fields["output_sha256"])):
        raise ValueError("output_sha256 must be 64 lowercase hex characters")
    for k, v in fields.items():  # a hash can contain a long digit run that looks like a card number, so skip it
        if k != "output_sha256" and isinstance(v, str) and find_leaks(v):
            raise ValueError(f"field '{k}' looks like it contains sensitive data; log a reference, not the data")
    records = read(path)
    if kind == "decision":
        if fields["approver"].strip().lower() in NOT_HUMAN:
            raise ValueError("approver must be a named person")
        if fields["decision"] not in DECISIONS:
            raise ValueError(f"decision must be one of {sorted(DECISIONS)}")
        if not any(r["seq"] == fields["ref"] and r["kind"] == "recommendation" for r in records):
            raise ValueError(f"ref {fields['ref']} is not an existing recommendation")
    rec = {"seq": len(records) + 1, "ts": now or datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "kind": kind, **fields, "prev_hash": records[-1]["hash"] if records else ZERO}
    rec["hash"] = _digest(rec)
    with open(path, "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def verify(path):
    """Return a list of problems; empty means the chain is intact."""
    problems, prev, recommendations = [], ZERO, set()
    lines = [ln for ln in pathlib.Path(path).read_text().splitlines() if ln.strip()]
    for i, line in enumerate(lines, 1):
        try:
            rec = json.loads(line)
        except ValueError:
            problems.append(f"record {i}: not valid JSON")
            continue
        if rec.get("seq") != i:
            problems.append(f"record {i}: sequence number is {rec.get('seq')}")
        if rec.get("prev_hash") != prev:
            problems.append(f"record {i}: does not follow the previous record")
        if rec.get("hash") != _digest(rec):
            problems.append(f"record {i}: contents changed after writing")
        if rec.get("kind") == "recommendation":
            recommendations.add(i)
        elif rec.get("kind") == "decision" and rec.get("ref") not in recommendations:
            problems.append(f"record {i}: decision refers to a missing recommendation")
        prev = rec.get("hash")
    return problems


def head(path):
    """Count and last hash. Store this somewhere separate to detect records removed from the end."""
    records = read(path)
    return {"count": len(records), "hash": records[-1]["hash"] if records else ZERO}
