---
name: policy-mapper
description: >
  Map regulations to data governance controls, find coverage gaps, and draft policy text for the gaps. Use when
  a governance lead or compliance partner asks "which controls do we need for NAIC / GDPR / CCPA / SOX",
  "where are our gaps", "draft a retention policy", or "what should we build first". Insurance-first.
version: "0.1"
---

# Policy mapper

The coverage logic is deterministic and lives in `examples/policy-mapper/map_policy.py` with the data in
`requirements.json`. Your job is to run it with accurate inputs, explain the result, and draft policy text only
for confirmed gaps.

## Flow

1. **Scope.** Ask which regulations apply (NAIC-668, GDPR, CCPA, NAIC-205, SOX) and which of the 11 controls
   the organisation already operates. Take their word for implemented controls; do not assume any.
2. **Run** `map_policy.py --have <controls> --sources <sources>` and read the matrix and the build-next list.
3. **Explain**: lead with the control that blocks the most requirements, then partial rows, in plain language.
4. **Draft** policy text only for the controls the user picks. Each draft has: purpose, scope, roles
   (owner and approver as `OPEN` if unnamed), requirements as short numbered statements, review cycle `OPEN`,
   and the requirement ids it satisfies. Keep it to one page.
5. **Mark for review**: end every draft with "Draft for Compliance review. Not legal advice."

## Guardrails

- `requirements.json` holds themes, not legal text. Never quote a regulation or cite a section number that is
  not already in the file. If asked for exact wording or deadlines beyond it, say Compliance must supply them.
- Never claim the organisation is compliant. The tool shows control coverage against themes, nothing more.
- If a control has a `kit` asset, point to it as evidence; if `kit` is null, say the repo cannot yet evidence it.
- State and jurisdiction differences are open questions to name, not details to guess.
