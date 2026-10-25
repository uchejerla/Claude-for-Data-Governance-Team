"""Synthetic P&C claims with a known number of injected defects (seeded, deterministic)."""
import random
from datetime import date, timedelta

STATES = ["TX", "CA", "FL", "NY", "OH", "IL"]
STATUSES = ["OPEN", "CLOSED", "DENIED", "REOPENED"]
LOBS = ["AUTO", "HOME", "COMMERCIAL"]

# defect name -> rows injected; the test asserts the runner finds exactly these
INJECTED = {
    "duplicate_claim_id": 5,
    "report_before_loss": 7,
    "invalid_state": 4,
    "paid_exceeds_claim": 6,
    "null_loss_date": 8,
    "invalid_status": 3,
}


def generate(n=500, seed=42):
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        loss = date(2025, 1, 1) + timedelta(days=rng.randrange(365))
        amt = round(rng.uniform(500, 50000), 2)
        rows.append({
            "claim_id": f"CLM{i:06d}",
            "policy_id": f"POL{rng.randrange(1, 200):05d}",
            "loss_date": loss.isoformat(),
            "report_date": (loss + timedelta(days=rng.randrange(0, 30))).isoformat(),
            "claim_status": rng.choice(STATUSES),
            "claim_amount": amt,
            "paid_amount": round(amt * rng.uniform(0, 1), 2),
            "state": rng.choice(STATES),
            "line_of_business": rng.choice(LOBS),
        })
    # each defect touches its own disjoint slice so counts stay exact
    idx = iter(rng.sample(range(5, n), sum(INJECTED.values())))
    for _ in range(INJECTED["duplicate_claim_id"]):
        rows[next(idx)]["claim_id"] = rows[0]["claim_id"]
    for _ in range(INJECTED["report_before_loss"]):
        r = rows[next(idx)]
        r["report_date"] = (date.fromisoformat(r["loss_date"]) - timedelta(days=3)).isoformat()
    for _ in range(INJECTED["invalid_state"]):
        rows[next(idx)]["state"] = "ZZ"
    for _ in range(INJECTED["paid_exceeds_claim"]):
        r = rows[next(idx)]
        r["paid_amount"] = round(r["claim_amount"] * 1.5, 2)
    for _ in range(INJECTED["null_loss_date"]):
        rows[next(idx)]["loss_date"] = None
    for _ in range(INJECTED["invalid_status"]):
        rows[next(idx)]["claim_status"] = "PENDING??"
    return rows
