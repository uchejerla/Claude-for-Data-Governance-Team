import pathlib
import re
import unittest

from validate_term import validate

HERE = pathlib.Path(__file__).parent
GOOD = (HERE / "good-open-claim.md").read_text()
BAD = (HERE / "bad-active-customer.md").read_text()
TEMPLATE = (HERE.parent.parent / "skills/define-business-term/assets/term-proposal.md").read_text()
GOOD_DEFINITION = "A reported loss under an in-force insurance policy for which the insurer has not yet made final payment or closed the file."


def ids(text):
    return {i for i, _, _ in validate(text)["findings"]}


def set_meta(text, key, value):
    return re.sub(rf'^{key}: .*$', f'{key}: "{value}"', text, flags=re.M)


def set_section(text, name, body):
    return re.sub(rf"(^## {name}\n)(.*?)(?=^## |\Z)", lambda m: f"{m.group(1)}\n{body}\n\n", text, flags=re.S | re.M)


class ValidatorTest(unittest.TestCase):
    def test_good_term_is_ready(self):
        r = validate(GOOD)
        self.assertEqual((r["findings"], r["verdict"]), ([], "ready-for-review"))

    def test_bad_term_fails_expected_checks_and_claim_is_flagged(self):
        r = validate(BAD)
        self.assertEqual(r["verdict"], "not-publishable")
        self.assertEqual(ids(BAD), {"B1", "B2", "B3", "B4", "B5", "B6", "B7", "M1", "M2", "M3", "M7"})
        self.assertNotEqual(r["claimed"], r["verdict"])

    def test_unfilled_skill_template_is_not_publishable(self):
        r = validate(TEMPLATE)
        self.assertEqual(r["verdict"], "not-publishable")
        self.assertIn("B0", ids(TEMPLATE))

    def test_each_blocker_triggers_on_its_own(self):
        cases = {
            "B0": set_section(GOOD, "Definition", ""),
            "B1": set_section(GOOD, "Source evidence", ""),
            "B2": GOOD.replace("A reported loss", "An open claim that is a reported loss"),
            "B3": set_meta(GOOD, "scope", "OPEN"),
            "B4": re.sub(r"(\*\*Threshold:\*\*).*", r"\1", GOOD.replace("A reported loss", "A current reported loss")),
            "B5": set_meta(set_meta(set_meta(GOOD, "steward", "OPEN"), "sme", "OPEN"), "approver", "OPEN"),
            "B6": set_meta(GOOD, "duplicate_check", ""),
            "B7": GOOD.replace("the file.", "the file in the claims_header table."),
        }
        for want, text in cases.items():
            self.assertEqual(ids(text), {want}, want)

    def test_open_threshold_and_open_definition_are_allowed(self):
        text = GOOD.replace("A reported loss", "A current reported loss").replace("None. Status-based: a claim", "OPEN: a claim")
        self.assertEqual(ids(text), set())

    def test_major_checks(self):
        self.assertEqual(ids(set_section(GOOD, "Examples", "| | Example | Why |\n| --- | --- | --- |\n| Positive | one | x |")), {"M2"})
        self.assertEqual(ids(GOOD.replace("closed the file.", "closed the file. It is one. It is two. It is three.")), {"M5"})
        self.assertEqual(validate(GOOD.replace("**Out of scope:** Incidents", "**Out of scope:** \n\n**x:** Incidents"))["verdict"], "needs-work")

    def test_two_majors_is_needs_work_and_never_ready(self):
        text = set_meta(set_section(GOOD, "Contrasting terms", ""), "sensitivity", "")
        self.assertEqual((ids(text), validate(text)["verdict"]), ({"M3", "M7"}, "needs-work"))


if __name__ == "__main__":
    unittest.main()
