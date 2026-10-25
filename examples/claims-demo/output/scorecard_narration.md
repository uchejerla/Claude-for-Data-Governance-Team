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
| Timeliness | `[NEEDS INPUT]` | none | No rule yet |

Overall: 98.9% (simple average of the six rule scores). 2 of 6 rules pass. 33 of 500 rows (6.6%) fail at least one rule, and no row fails two, so cleaning 33 rows would bring every rule to 100%.

Health status: 🟡 Needs Attention.

## Headline

Claims data is 93% clean row by row, but four of six rules fail their strict targets, including a duplicate-ID and an impossible-date problem that matter for reserve reporting.

## Executive narrative (CDO, 30 seconds)

The first claims quality check shows 98.9% overall, which sounds healthy, but the failures are in the places that matter most. Five claims are duplicated and seven were reported before the loss happened; both distort reserve and filing numbers. Six claims show more paid than claimed, which is a leakage and conduct risk. The problems are limited to 33 records, so a targeted clean-up is realistic. Decision needed: name an owner for claim header data and approve fixes at the source.

## Operational narrative (stewardship and Data Engineering)

Scores by rule: CLM-001 uniqueness 99.0% (5 extra rows on one claim ID), CLM-002 completeness 98.4% (8 null `loss_date`), CLM-003 consistency 98.6% (7 rows with `report_date` before `loss_date`), CLM-004 validity 99.2% (4 invalid state codes), CLM-005 validity 99.4% (3 invalid statuses), CLM-006 accuracy 98.8% (6 rows with `paid_amount` above `claim_amount`). The two validity rules pass only because their threshold is 99%; the other four need 100% and fail. The defects do not overlap, so each has an independent cause to find. Data Engineering should first compare the 6 rows sharing a claim ID and check whether the 7 impossible dates share a constant gap. Timeliness is unmeasured: no rule exists for the FNOL acknowledgment SLA.

## Trend commentary

`[NEEDS INPUT]` No prior-period scores were provided. Run the scorecard again after remediation to create the first comparison.

## Top wins

`[NEEDS INPUT]` No remediation has happened yet. Baseline only.

## Top risks

1. Duplicate claim IDs (CLM-001), risk of double counting.
2. Impossible FNOL sequence (CLM-003), risk to FNOL timeliness reporting.
3. Overpayment signal (CLM-006), leakage and payment accuracy.

## Talking points

- This is the baseline: 98.9% overall, 33 of 500 rows affected.
- The score hides risk: the strict rules all fail and they cover reserves and payments.
- Everything found is fixable: 33 non-overlapping records.
- Timeliness is a blind spot until we add a rule.
- Ask: assign an owner for claim header data.

## Recommended actions

1. Triage cards 1 and 2 first (Critical); see `triage_cards.md`.
2. Add a timeliness rule (FNOL acknowledgment within 24 hours) so all six dimensions are measured.
3. Re-run the scorecard after fixes to start the trend.

*Skill version: goviq-claims-dq-scorecard-narration-v1. Thresholds in `rules.json` are demo values, not company standards.*
