---
term: "Open Claim"
artifact_type: term
status: ready-for-review
verdict: ready-for-review
confidence: low
rubric_score: "n/a"
domain: "Claims / Claim lifecycle"
scope: "Enterprise, US personal lines auto and home"
steward: "A. Patel (example name)"
sme: "OPEN"
approver: "R. Gomez (example name)"
duplicate_check: "Searched glossary and claims report library (example); no exact match; one near-duplicate: Pending Claim"
sensitivity: "regulated"
last_updated: "2026-10-25"
---

# Term proposal: Open Claim

> Synthetic example for the validator. Names and sources are fictional.

## Definition

A reported loss under an in-force insurance policy for which the insurer has not yet made final payment or closed the file.

## Boundary

**In scope:** Reported losses on US personal auto and homeowners policies, including reopened claims.

**Out of scope:** Incidents reported for information only with no claim opened (use *Incident Report*); commercial lines (use *Commercial Open Claim*).

**Threshold:** None. Status-based: a claim is open from first notice of loss until closure.

## Examples

| | Example | Why this one |
| --- | --- | --- |
| Positive | Auto collision reported Monday, adjuster assigned, no payment yet | Reported, not paid, not closed |
| Positive | Closed home claim reopened after new damage found | Reopened claims are open again |
| Negative | Claim fully paid and closed last month | Closest near-miss: it was open earlier but is now closed |

## Contrasting terms

| Term | Difference from this term |
| --- | --- |
| Pending Claim | Pending means coverage is still being decided; an open claim has been accepted for handling |
| Closed Claim | Closed means the file is shut; an open claim still has work or payments outstanding |

## Calculation or logic

## Assumptions

- Legal entity: single US insurer
- Currency / fiscal calendar / time zone: USD, calendar year, US Eastern
- Treatment of internal, test and employee records: excluded

## Flags

- **Sensitivity:** regulated: claim records carry claimant personal data and feed statutory reporting
- **Jurisdiction dependency:** state reporting windows differ
- **Downstream dependency:** open claim counts in reserve reports (example)

## Source evidence

Claims Handling Standard (internal, example reference). SME confirmation pending, so confidence is low.

## Duplicate and homonym check

- **Surface searched:** glossary, claims report library (example)
- **Exact matches:** none
- **Synonyms:** outstanding claim
- **Near-duplicates (different scope):** Pending Claim
- **Homonyms (same label, other domain):** none found

## Open questions

1. For Claims Ops (A. Patel): is a claim with a closing payment but an open subrogation recovery still open?

## Approval recommendation

Ready for review. R. Gomez is asked to decide whether subrogation keeps a claim open.
