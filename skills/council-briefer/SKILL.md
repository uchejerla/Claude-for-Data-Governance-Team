---
name: council-briefer
description: >
  Prepare the monthly data governance council brief from metrics: numbers, changes, flags, and decisions. Use
  when a governance lead asks "prepare the council deck", "summarise this month's governance metrics", or
  provides DQ scores, CDE coverage, glossary progress, open issues and access request counts.
version: "0.1"
---

# Council briefer

`examples/council-brief/make_brief.py` computes the facts (changes versus prior, SLA breaches, coverage gaps).
You add a short story around them. Facts come from the tool; the story must not add any.

## Flow

1. **Collect metrics** in the `metrics_sample.json` format: current and prior period figures, open issues with
   severity and age, SLA days, CDE coverage target, and the decisions the council is being asked to make.
   Missing prior period: say trend is unavailable.
2. **Run** `make_brief.py metrics.json`.
3. **Write the narrative** above the tool output, at most:
   - a one-sentence headline that leads with business meaning, not a score;
   - three bullets: biggest improvement, biggest risk, what changes if the council decides nothing;
   - the "Needs attention" and "Decisions needed" sections unchanged from the tool.
4. **Offer follow-ups**: for each flagged issue, a triage card (`goviq-claims-dq-triage`); for the numbers, a
   fuller narration (`goviq-claims-dq-scorecard-narration`).

## Guardrails

- Every number in the narrative must appear in the tool output. If you want a number that is not there, ask for it.
- Never create decisions. Decisions come from the user's input only.
- Say plainly when a figure is synthetic or a demo value.
- Targets and SLAs are the company's; flag any that look like defaults.
