# Triage cards: claims DQ demo

Produced by applying `skills/goviq-claims-dq-triage` to the failing rules in the scorecard from `run_dq.py`. Anchor for all cards: synthetic data, SQLite in-memory, table `claims`, 500 rows. Fields the scorecard cannot support are `[NEEDS INPUT]`; nothing is invented. A steward must confirm severity before these are logged.

Passing rules CLM-004 (4 bad state codes) and CLM-005 (3 bad statuses) are within their 99% thresholds and need no card, but the bad values should still be cleaned.

---

## Card 1: CLM-003, report date before loss date

- **Issue:** 7 claims were reported before the loss they report (`report_date < loss_date`).
- **Classification:** Domain Claims. Subdomain FNOL. Table `claims`. Columns `report_date`, `loss_date`. Source system `[NEEDS INPUT]`.
- **DQ dimension:** Consistency (rule dimension). The skill's known-pattern table lists this sequence as Accuracy; steward to confirm which label the program uses.
- **Matches known pattern:** "FNOL date is after loss date (impossible sequence)", the same impossible-sequence defect in reverse. Typical severity per skill: Critical.
- **Severity:** 🔴 Critical (pattern default). Records affected: 7 of 500 (1.4%). Regulatory risk: State Fast Track timeliness reporting and Market Conduct, since FNOL timing drives both. Business impact `[NEEDS INPUT]`.
- **Root causes:** (1) Date keyed or imported with day/month or time-zone swap. (2) Loss date back-filled wrongly after adjuster review. (3) Report date defaulted to a system date at migration.
- **Next action:** Today: list the 7 rows with `WHERE report_date < loss_date` and check whether the gap is a constant (suggests a systematic cause). Short term: add a validation on entry for the FNOL form.
- **Escalation:** Stay with steward until the gap pattern is known; escalate to Data Engineering if constant.

## Card 2: CLM-001, duplicate claim IDs

- **Issue:** 5 extra rows reuse an existing `claim_id` (6 rows share one ID).
- **Classification:** Subdomain: cross-cutting (claim header). Column `claim_id`. Dimension Uniqueness.
- **Matches known pattern:** "Duplicate claim numbers". Typical severity: Critical.
- **Severity:** 🔴 Critical. Records affected: 5 extra rows (1.0%). Risk: double counting in reserves and payments, which feeds Schedule P. Dollar impact `[NEEDS INPUT]`.
- **Root causes:** (1) Re-ingestion without a merge key. (2) Same claim loaded from two source systems. (3) Reopened claim created as a new row.
- **Next action:** Today: compare the 6 rows field by field to see if they are true copies or different claims. Short term: enforce a unique constraint or dedupe step at load.
- **Escalation:** Data Engineering if they are true copies.

## Card 3: CLM-006, paid amount above claim amount

- **Issue:** 6 claims show `paid_amount` greater than `claim_amount`.
- **Classification:** Subdomain Payments. Columns `paid_amount`, `claim_amount`. Dimension Accuracy.
- **Pattern note:** The nearest known pattern is "payment exceeding policy coverage limits" (Critical). This rule compares to the claimed amount, not the limit, and the demo has no limit field, so I rate it one level lower.
- **Severity:** 🟠 High. Records affected: 6 of 500 (1.2%). Risk: overpayment leakage and Market Conduct payment accuracy. Dollar impact `[NEEDS INPUT]`.
- **Root causes:** (1) Supplemental payments added without updating the claim amount. (2) Duplicate payment postings. (3) Currency or unit mismatch.
- **Next action:** Today: sum the excess (`paid_amount - claim_amount`) on the 6 rows and check for duplicate payment lines. Short term: add a payment-vs-reserve control.
- **Escalation:** Compliance if any excess is confirmed as overpayment.

## Card 4: CLM-002, missing loss date

- **Issue:** 8 claims have no `loss_date`.
- **Classification:** Subdomain FNOL. Column `loss_date`. Dimension Completeness.
- **Pattern note:** Not in the skill's table directly. It blocks the "loss date outside policy period" check, so it hides other defects.
- **Severity:** 🟠 High. Records affected: 8 of 500 (1.6%), the largest single count. Risk: coverage verification and Market Conduct.
- **Root causes:** (1) Optional field on the intake form. (2) Source feed drops the field for one channel. (3) Placeholder converted to NULL at load.
- **Next action:** Today: group the 8 rows by source/channel if available (`[NEEDS INPUT]`: no source column in the demo table). Short term: make the field mandatory at intake.
- **Escalation:** Stay with steward.

---

**Follow-up questions (max 2, per the skill):** Are the 33 failing rows concentrated in one source system or load date? Which downstream reports use `claim_id` and `paid_amount`?

*Assumptions:* severity for Cards 3 and 4 is my judgment, flagged above. Triage date and skill version: goviq-claims-dq-triage-v1.
