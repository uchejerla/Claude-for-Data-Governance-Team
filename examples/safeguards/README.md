# Safeguards: masking and audit log

Two building blocks behind `docs/guardrails.md`. Python 3 standard library only. Tested on synthetic data; neither is wired into a live Claude call or a real pipeline yet.

```bash
python3 -m unittest -v
```

## Masking (`mask.py`)

Run it on records before they are shown to Claude.

1. Columns tagged sensitive by name (`tag_sensitivity.py`) become keyed tokens such as `GOV_ID:7270a879a1`. The same value always gets the same token for a given key, so joins and counts still work; without the key nothing can be reversed. A key is required and there is no default.
2. Free-text columns (notes, description, comments...) become `[REDACTED_FREE_TEXT]`. `scrub_free_text=True` scrubs patterns instead.
3. Every other string cell is scrubbed for SSNs, emails, phone numbers and card numbers (cards need a valid checksum).
4. `assert_no_leaks(rows)` is the gate before sending. It raises and names the row, column and kind, never the value.

The report counts what was masked per column and contains no values.

## Audit log (`audit.py`)

An append-only JSON-lines file. A `recommendation` record says what a tool or Claude proposed (who asked, which skill and version, a reference to the input, a hash of the output). A later `decision` record names the human who approved, rejected or deferred it and points back by `ref`.

- Each record includes the hash of the one before. `verify(path)` reports edits, deleted records, reordered records and decisions that point at nothing.
- Raw sensitive data cannot be logged: fields are checked with the same leak patterns, so log a reference, not the data. Unknown fields are refused.
- The approver must be a named person ("Claude", "system" and similar are refused).
- `head(path)` returns the record count and last hash. Store it somewhere separate.

## Limits, on purpose

- Person names inside free text are not detected. That is why free text is redacted by default. A test documents it.
- Tagging is by column name, so an oddly named sensitive column is only caught if its values match a pattern.
- Removing records from the end of the log is only detectable against a stored `head()`. One writer, no file locking.
- Not independently reviewed. Use a reviewed PII detection service and an append-only store before real data.
