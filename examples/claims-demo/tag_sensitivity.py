"""Tag columns as GOV_ID / PII / PHI / FINANCIAL_ACCOUNT from their names only.

shortcut: name-based, no data sampling, so it misses oddly named columns and cannot confirm a hit;
upgrade to value-pattern checks on masked samples before trusting it beyond a first pass.
"""
import re
import sys

PERSON = ["claimant", "insured", "customer", "driver", "adjuster", "first", "last", "full",
          "middle", "beneficiary", "witness", "attorney", "employee"]

# tag -> token sets; a column hits when it contains every token of any one set
RULES = {
    "GOV_ID": [{"ssn"}, {"social", "security"}, {"passport"}, {"tin"}, {"itin"},
               {"license"}, {"licence"}],
    "PII": [{"dob"}, {"birth"}, {"email"}, {"phone"}, {"mobile"}, {"address"},
            {"fullname"}, {"firstname"}, {"lastname"}] + [{p, "name"} for p in PERSON],
    "PHI": [{"diagnosis"}, {"icd"}, {"injury"}, {"medical"}, {"treatment"}, {"prescription"}],
    "FINANCIAL_ACCOUNT": [{"bank", "account"}, {"routing"}, {"iban"}, {"cvv"},
                          {"credit", "card"}, {"card", "number"}],
}


def tokens(column):
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", column)  # camelCase -> words
    return {t.lower() for t in re.findall(r"[A-Za-z]+|\d+", spaced)}


def tag_columns(columns):
    """Return {column: sorted tags}; empty list means no sensitivity detected from the name."""
    out = {}
    for c in columns:
        toks = tokens(c)
        out[c] = sorted(tag for tag, sets in RULES.items() if any(s <= toks for s in sets))
    return out


SAMPLE = ["claim_id", "policy_id", "claimant_name", "claimant_ssn", "claimant_dob",
          "driver_license_no", "injury_description", "icd10_code", "bank_account_no",
          "email_address", "loss_date", "claim_amount", "state", "product_name"]

if __name__ == "__main__":
    cols = sys.argv[1:] or SAMPLE
    print("| Column | Tags |\n|---|---|")
    for col, tags in tag_columns(cols).items():
        print(f"| {col} | {', '.join(tags) or '-'} |")
    print("\nName-based first pass only. A steward must review before any tag is applied.")
