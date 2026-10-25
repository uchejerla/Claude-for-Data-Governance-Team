# Guardrails

How this kit keeps Claude's work safe to rely on in a governance program. For each guardrail this page says what it is, whether it is **enforced by tested code**, **instructed in a skill** (model behaviour, not a guarantee), or **not built yet**. If you are reviewing this for security, read section 3 and section 7 first.

## 1. Principles

1. **Claude proposes, a named person decides.** No tool or skill approves, publishes, grants access or changes a catalog.
2. **Numbers come from code, not from the model.** Scores, counts, changes and flags are computed by tested scripts. Claude explains them.
3. **Unknown stays unknown.** Missing facts are marked `NEEDS INPUT` or `OPEN`, never filled with plausible text.
4. **Fail closed.** When input is unknown or incomplete, tools deny or stop; they do not guess a permissive answer.
5. **Least data.** Claude gets metadata, column names, counts and results, not raw sensitive values.

## 2. Guardrail status

| # | Guardrail | Status | Evidence |
|---|---|---|---|
| 1 | Tools only recommend; they never approve or grant | Enforced by tested code | `review_access.py` returns `recommend-approve` / `pending-conditions` / `deny`; `validate_term.py` returns `ready-for-review`, never "approved"; tests in `examples/access-review`, `examples/glossary-validator` |
| 2 | Access review fails closed | Enforced by tested code | Unknown role denies; unknown tag, missing field or non-positive days raise an error (`test_access.py`) |
| 3 | Strictest rule wins on mixed sensitivity | Enforced by tested code | Every tag's tier is checked (`test_strictest_tier_wins_for_mixed_tags`) |
| 4 | Rules from outside the repo cannot write files | Enforced by tested code | `run_dq.py` rejects any `fail_sql` that is not a SELECT (`test_non_select_rule_rejected`). A prefix check, not full SQL parsing: still read rules before running them |
| 5 | Missing metadata is never read as "safe" or "not critical" | Enforced by tested code | CDE identifier returns `needs metadata`, not `not a CDE` (`test_cde.py`) |
| 6 | Council brief invents no decisions or figures | Enforced by tested code | Decisions render only from input; flags are computed (`test_brief.py`) |
| 7 | Mismatched self-reported status is flagged | Enforced by tested code | Validator reports a file whose own `verdict:` disagrees with the result |
| 8 | Regulation themes are not presented as legal text | Documented, partly enforced | Notice printed on every policy-mapper run and in the README; the wording itself is not legally reviewed |
| 9 | Claude must not fabricate and must cite inputs | Instructed in skills | "Never fabricate" and `NEEDS INPUT` rules in the skills; a model can still err, so a steward reviews |
| 10 | Sensitivity tagging uses names only | Enforced by design | `tag_sensitivity.py` reads column names; no values are read or sent |
| 11 | Read-only connectors first, writes as drafts | Not built | No connector exists yet; this is the rule it must follow (section 6) |
| 12 | Audit trail of recommendations and named-human decisions | Library built and tested; not wired into a live workflow | `examples/safeguards/audit.py`: hash-chained log, tampering and unnamed approvers detected, sensitive data refused. Does not log prompts or outputs themselves, only references and hashes |
| 13 | Masking of sensitive values before anything reaches the model | Library built and tested; not wired into a live pipeline | `examples/safeguards/mask.py`: keyed tokens, free text redacted, pattern scrub, leak gate. Person names in free text and oddly named columns are not detected |

## 3. Data handling: what may reach Claude

| May be sent | Never sent |
|---|---|
| Table and column names, descriptions, owners | Raw SSNs, government or driver licence numbers |
| Counts, rates, scores, rule results | Health details tied to a person (diagnosis text, injury notes) |
| Aggregate profiles (null %, distinct count, min/max of non-sensitive fields) | Bank account, card or routing numbers |
| Lineage graphs and catalog metadata | Free-text claim notes and adjuster notes |
| Masked or synthetic sample rows | Any real claimant record that has not been masked |

Rules for a deployment:
- Run profiling and DQ rules inside the customer's environment and share only the results.
- Where a sample is needed for classification, mask it first and keep the original out of the conversation.
- Do not paste real claimant data into a chat to "test" a skill. Use the synthetic data in `examples/`.
- Confirm retention and training terms in the customer's own agreement with Anthropic. This repo makes no claim about them.

Status: the tools in this repo work only on synthetic data and metadata. `examples/safeguards/mask.py` implements the masking and the leak gate this table calls for, and is tested on synthetic records. Running it on real data, in the customer's environment, ahead of every Claude call, is deployment work that is not built.

## 4. Who approves what

| Output | Claude may | A named person must |
|---|---|---|
| Glossary term | Draft, score against the rubric | Approve (steward, then approver) |
| CDE list | Rank with reasons | Confirm each CDE and its owner |
| DQ rules and thresholds | Draft, run, report | Agree thresholds, set severity |
| Sensitivity tags | Suggest from names | Confirm before any tag is applied |
| Access request | Recommend with reasons | Decide (data owner) |
| Policy text | Draft for confirmed gaps | Compliance review; no legal reliance on drafts |
| Council brief | Compute facts, draft narrative | Choose and own the decisions |

## 5. Audit trail (library built, not wired in)

`examples/safeguards/audit.py` records each Claude-assisted decision as two linked entries: a recommendation (timestamp, requester, skill and version, input reference, hash of the tool output, the recommendation) and a decision (the named approver, the decision, the time). Entries are hash-chained, so edits, deletions and reordering are detected; raw sensitive data and unnamed approvers are refused.

Still needed for a deployment:
- Call it from the real workflow, so every recommendation is logged automatically.
- Store the log outside the chat and keep it for the customer's records-retention period.
- Keep `head()` (count and last hash) in a separate place: removing records from the end of the file is only detectable against it.
- Use an append-only or write-once store for multiple writers; the file version has one writer and no locking.

## 6. Connector rules (for the Collibra work)

- Read-only first; prove the review workflow before any write.
- Writes create draft assets or proposals that a person approves in the catalog. Never auto-approve.
- Scoped service credentials, least privilege, stored in the customer's secret manager. No credentials in this repo or in chat.
- Log every call (section 5).
- Test against a non-production catalog first.

## 7. Known limits

- Skills are instructions, not enforcement. A model can still produce a wrong or over-confident explanation; the controls are the tested tools, the review step and the named approver.
- The scoring weights, access policy, SLAs and thresholds are demo values until the customer sets them.
- The policy mapper's regulation themes are plain-language summaries. Compliance must confirm applicability and wording.
- The sensitivity tagger misses oddly named columns and cannot confirm a hit.
- Nothing here has run on real data or a real catalog, and nothing has had an independent security review.

## 8. Questions a buyer's security team will ask

| Question | Answer today |
|---|---|
| Can Claude change our catalog or grant access? | No. The tools only recommend; no connector exists yet |
| Does sensitive data reach the model? | Not in this repo (synthetic data only). In a deployment, section 3 applies; a masking and leak-gate library is built and tested but not wired into a pipeline |
| Is there an audit log? | A tamper-evident log library is built and tested; it is not wired into a live workflow yet (section 5) |
| Is it independently tested or certified? | No |
| Where does our data go? | Depends on deployment and your Anthropic agreement; not decided here |
| What happens when input is wrong or missing? | Tools stop or fail closed; unknowns are marked, not guessed |
