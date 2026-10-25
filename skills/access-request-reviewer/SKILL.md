---
name: access-request-reviewer
description: >
  Review a data access request against a tiered policy and recommend approve, pending conditions, or deny, with
  reasons. Use when a steward or data owner asks "should we grant this access", "review this request", or pastes
  an access request with a role, dataset, purpose and duration. Insurance-first (claimant PII, SSNs, health data).
version: "0.1"
---

# Access request reviewer

The decision logic is deterministic: `examples/access-review/review_access.py` against `policy.json`.
You gather the facts, run it, and explain the outcome. You never grant access.

## Flow

1. **Collect the request fields**: requester, role, dataset, purpose, days, sensitivity tags, training complete,
   owner approved. Get the tags from the catalog or from `examples/claims-demo/tag_sensitivity.py`; if the
   dataset's tags are unknown, ask rather than assume "none".
2. **Run** `review_access.py requests.json`.
3. **Explain the result**:
   - `recommend-approve`: say which policy points were met.
   - `pending-conditions`: list what the requester still needs (training, owner approval) and who supplies it.
   - `deny`: give each reason and the smallest change that could make a new request valid (shorter duration,
     a role that is allowed, a stated purpose).
4. **Route**: a named data owner makes the final decision. Name that role in the reply.

## Guardrails

- Recommendation only. Never write "access granted".
- Fail closed: unknown role denies, unknown tag stops the review, missing fields stop the review.
- `policy.json` is a demo policy. Replace it with the company's own before real use, and say so when asked
  whether a request "complies with policy".
- Do not echo sensitive values from the request into the reply.
