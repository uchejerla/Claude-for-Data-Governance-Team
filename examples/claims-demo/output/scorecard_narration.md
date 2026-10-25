# Scorecard narration: claims DQ demo

Produced by applying `skills/goviq-claims-dq-scorecard-narration` to the `run_dq.py` scorecard. Scope: synthetic table `claims`, 500 rows, audience CDO and governance committee. No prior period and no event history exist, so there is no trend section and no "wins". Those are `[NEEDS INPUT]`, not guessed.

## Score summary

| Dimension | Current | Rules | Status |
|---|---|---|---|
| Uniqueness | 99.0% | CLM-001 | Below 100% target |
| Completeness | 98.4% | CLM-002 | Below 100% target |
| Consistency | 98.6% | CLM-003 | Below 100% target |
| Validity | 99.3% (avg of 99.2% and 99.4%) | CLM-004, CLM-005 | Both within 99% target |
| Accuracy | 98.8% | CLM-006 | Below 100% target |
| Timeliness | 98.2% | CLM-007 | Below 99% target |

Overall: 98.8% (simple average of the seven rule scores). 2 of 7 rules pass. 42 of 500 rows (8.4%) fail at least one rule, and no row fails two, so cleaning 42 rows would bring every rule to 100%.

Health status: 🟡 Needs Attention.

## Headline

Claims data is 92% clean row by row, but five of seven rules miss their targets, including a duplicate-ID and an impossible-date problem that matter for reserve reporting, and late reporting that is now measured for the first time.

## Executive narrative (CDO, 30 seconds)

The first claims quality check shows 98.8% overall, which sounds healthy, but the failures are in the places that matter most. Five claims are duplicated and seven were reported before the loss happened; both distort reserve and filing numbers. Nine claims were reported more than 30 days after the loss, which puts state reporting windows at risk. Six claims show more paid than claimed, which is a leakage and conduct risk. The problems are limited to 42 records, so a targeted clean-up is realistic. Decision needed: name an owner for claim header data and approve fixes at the source.

## Operational narrative (stewardship and Data Engineering)

Scores by rule: CLM-001 uniqueness 99.0% (5 extra rows on one claim ID), CLM-002 completeness 98.4% (8 null `loss_date`), CLM-003 consistency 98.6% (7 rows with `report_date` before `loss_date`), CLM-004 validity 99.2% (4 invalid state codes), CLM-005 validity 99.4% (3 invalid statuses), CLM-006 accuracy 98.8% (6 rows with `paid_amount` above `claim_amount`), CLM-007 timeliness 98.2% (9 rows reported more than 30 days after the loss). The two validity rules pass only because their threshold is 99%; the other five miss theirs. The defects do not overlap, so each has an independent cause to find. Data Engineering should first compare the 6 rows sharing a claim ID, check whether the 7 impossible dates share a constant gap, and check whether the 9 late reports come from one channel. The 30-day window in CLM-007 is a demo value; the real FNOL acknowledgment SLA and state deadlines should replace it.

## Trend commentary

`[NEEDS INPUT]` No prior-period scores were provided. Run the scorecard again after remediation to create the first comparison.

## Top wins

`[NEEDS INPUT]` No remediation has happened yet. Baseline only.

## Top risks

1. Duplicate claim IDs (CLM-001), risk of double counting.
2. Impossible FNOL sequence (CLM-003), risk to FNOL timeliness reporting.
3. Late reporting (CLM-007), risk of missing state reporting windows.
4. Overpayment signal (CLM-006), leakage and payment accuracy.

## Talking points

- This is the baseline: 98.8% overall, 42 of 500 rows affected.
- The score hides risk: the strict rules all fail and they cover reserves and payments.
- All six dimensions are now measured, including timeliness.
- Everything found is fixable: 42 non-overlapping records.
- Ask: assign an owner for claim header data and confirm the real reporting deadline.

## Recommended actions

1. Triage cards 1 and 2 first (Critical); see `triage_cards.md`.
2. Replace the demo 30-day window with the company's FNOL SLA and state deadlines.
3. Re-run the scorecard after fixes to start the trend.

*Skill version: goviq-claims-dq-scorecard-narration-v1. Thresholds in `rules.json` are demo values, not company standards.*
