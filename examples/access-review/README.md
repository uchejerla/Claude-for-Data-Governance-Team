# Access request reviewer

Checks a data access request against a tiered policy (`policy.json`) and recommends `recommend-approve`, `pending-conditions` or `deny`, with reasons. Python 3 standard library only.

```bash
python3 review_access.py requests_sample.json
python3 -m unittest -v
```

- Tiers by sensitivity: none, PII, and special categories (GOV_ID, PHI, FINANCIAL_ACCOUNT). Each sets allowed roles, purpose, maximum days, training and data owner approval.
- Hard failures (wrong role, too long, no purpose) deny. Missing training or approval is pending, so the requester knows what to fix.
- Several tags on one dataset: every tier applies, so the strictest wins.
- Fails closed: unknown role denies; unknown tag, missing field or non-positive days raise an error.
- `policy.json` is a demo policy and the sample requesters are fictional. Replace the policy with the company's before real use. The tool recommends; a named data owner decides.
