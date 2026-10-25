# Glossary term validator

Checks a term proposal written in the `skills/define-business-term` template against the mechanical parts of its rubric. Python 3 standard library only.

```bash
python3 validate_term.py good-open-claim.md bad-active-customer.md   # exit code 1 if any file has a blocker
python3 -m unittest -v
```

What it checks (14 items): empty definition; evidence; circular wording (B2); scope; vague words without a threshold; named owner; duplicate check recorded; table/column/SQL in the definition; boundary; examples (2 positive, 1 negative); two contrasting terms; definition length; sensitivity; label format.

Verdict follows the rubric: any blocker is `not-publishable`, no blockers and no majors is `ready-for-review`, otherwise `needs-work`. It also flags a file whose own `verdict:` line disagrees (see `bad-active-customer.md`, which claims it is ready).

Limits, on purpose:
- Judgement items are not checked: synonym or two-way circularity, atomic, plain language, real vs. invented examples, whether the evidence actually supports the claims.
- Circularity only catches the term repeated after the opening "X is ...".
- "Ready for review" means ready for a human approver, not approved.

Both sample terms are synthetic; names and sources are fictional.

Next step toward Collibra: the same fields map to a Collibra term asset (definition, domain, owner, status), so a connector can later push validated terms as drafts.
