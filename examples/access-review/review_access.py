"""Recommend approve / pending-conditions / deny for a data access request against a tiered policy.

The result is a recommendation with reasons; a named data owner makes the decision.
Fails closed: an unknown role denies, an unknown sensitivity tag is an error, a missing field is an error.
Usage: python3 review_access.py requests.json
"""
import json
import pathlib
import sys

POLICY = json.loads((pathlib.Path(__file__).parent / "policy.json").read_text())
REQUIRED = ("requester", "role", "dataset", "purpose", "days", "tags", "training_complete", "owner_approved")


def review(req, policy=POLICY):
    missing = [k for k in REQUIRED if k not in req]
    if missing:
        raise ValueError(f"request missing fields: {missing}")
    if req["days"] <= 0:
        raise ValueError("days must be positive")
    unknown = [t for t in req["tags"] if t not in policy["tiers"]]
    if unknown:
        raise ValueError(f"unknown sensitivity tags: {unknown}")
    denied, pending = [], []
    if req["role"] not in policy["roles"]:
        denied.append(f"role '{req['role']}' is not a recognised role")
    for tag in req["tags"] or ["none"]:
        t = policy["tiers"][tag]
        if t["roles"] != "*" and req["role"] not in t["roles"]:
            denied.append(f"{tag}: role '{req['role']}' may not access this tier")
        if t["purpose"] and not req["purpose"].strip():
            denied.append(f"{tag}: a business purpose is required")
        if req["days"] > t["max_days"]:
            denied.append(f"{tag}: {req['days']} days exceeds the {t['max_days']}-day limit")
        if t["training"] and not req["training_complete"]:
            pending.append(f"{tag}: privacy training not complete")
        if t["owner_approval"] and not req["owner_approved"]:
            pending.append(f"{tag}: data owner approval needed")
    decision = "deny" if denied else "pending-conditions" if pending else "recommend-approve"
    return {"requester": req["requester"], "dataset": req["dataset"], "decision": decision,
            "reasons": sorted(set(denied)) + sorted(set(pending))}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    for r in map(review, json.loads(pathlib.Path(sys.argv[1]).read_text())):
        print(f"{r['requester']} -> {r['dataset']}: {r['decision']}")
        for reason in r["reasons"]:
            print(f"  - {reason}")
    print("\nRecommendation only. A named data owner decides.")
