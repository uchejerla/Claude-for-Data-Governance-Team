"""Mask sensitive values before anything is shown to Claude, and check the result for leaks.

Layers: (1) columns tagged sensitive by name become keyed tokens, (2) free-text columns are redacted (or pattern-scrubbed
on request), (3) every other string cell is pattern-scrubbed, (4) assert_no_leaks() is the gate before sending.

shortcut: column-name tags plus regex, so person names inside free text and oddly named columns are not caught;
upgrade to a reviewed PII detection service before using real data.
"""
import hashlib
import hmac
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "claims-demo"))
from tag_sensitivity import tag_columns, tokens  # noqa: E402

FREE_TEXT = {"note", "notes", "description", "comment", "comments", "text", "narrative", "memo", "remarks"}


def _luhn(digits):
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch) * (2 if i % 2 else 1)
        total += n - 9 if n > 9 else n
    return total % 10 == 0


def _card(m):
    d = re.sub(r"\D", "", m.group())
    return "[CARD]" if 13 <= len(d) <= 19 and _luhn(d) else m.group()


# order matters: cards first so a long digit run is not mistaken for a phone number
PATTERNS = [
    ("CARD", re.compile(r"(?<!\d)\d(?:[ -]?\d){12,18}(?!\d)"), _card),
    ("SSN", re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"), "[SSN]"),
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL]"),
    ("PHONE", re.compile(r"(?<!\d)\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?!\d)"), "[PHONE]"),
]


def scrub(text):
    for _, rx, repl in PATTERNS:
        text = rx.sub(repl, text)
    return text


def find_leaks(text):
    """Kinds of sensitive-looking patterns present in the text (never the values themselves)."""
    return [kind for kind, rx, repl in PATTERNS if rx.sub(repl, text) != text]


def _token(key, tag, value):
    return f"{tag}:" + hmac.new(key.encode(), f"{tag}|{value}".encode(), hashlib.sha256).hexdigest()[:10]


def mask_rows(rows, key, scrub_free_text=False):
    """Return (masked rows, report). The report holds counts per column, never values."""
    if not key:
        raise ValueError("a masking key is required")
    tags = tag_columns(sorted({c for r in rows for c in r}))
    report = {"tokenised": {}, "redacted": {}, "scrubbed": {}}
    bump = lambda kind, col: report[kind].__setitem__(col, report[kind].get(col, 0) + 1)
    out = []
    for r in rows:
        m = {}
        for c, v in r.items():
            if v is None or v == "":
                m[c] = v
            elif tags[c]:  # sensitive by name: tokenise whatever type it is
                m[c] = _token(key, "+".join(tags[c]), v)
                bump("tokenised", c)
            elif isinstance(v, str) and tokens(c) & FREE_TEXT and not scrub_free_text:
                m[c] = "[REDACTED_FREE_TEXT]"
                bump("redacted", c)
            elif isinstance(v, str):
                m[c] = scrub(v)
                if m[c] != v:
                    bump("scrubbed", c)
            else:
                m[c] = v
        out.append(m)
    return out, report


def assert_no_leaks(rows):
    """Gate before sending to Claude: raise, naming row, column and kind (never the value), if anything leaks."""
    found = [f"row {i} column '{c}': {', '.join(k)}"
             for i, r in enumerate(rows) for c, v in r.items() if isinstance(v, str) and (k := find_leaks(v))]
    if found:
        raise ValueError("possible sensitive data in output: " + "; ".join(found))
