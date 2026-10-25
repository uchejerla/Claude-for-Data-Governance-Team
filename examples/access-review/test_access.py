import json
import pathlib
import unittest

from review_access import review

SAMPLE = json.loads((pathlib.Path(__file__).parent / "requests_sample.json").read_text())
BASE = SAMPLE[1]  # a valid PII request


def with_(**kw):
    return {**BASE, **kw}


class AccessTest(unittest.TestCase):
    def test_sample_decisions(self):
        got = [review(r)["decision"] for r in SAMPLE]
        self.assertEqual(got, ["recommend-approve", "recommend-approve", "pending-conditions",
                               "deny", "recommend-approve", "deny"])

    def test_untagged_data_needs_no_training_or_purpose(self):
        self.assertEqual(review(with_(tags=[], purpose="", training_complete=False))["decision"], "recommend-approve")

    def test_missing_training_is_pending_not_deny(self):
        r = review(with_(training_complete=False))
        self.assertEqual((r["decision"], r["reasons"]), ("pending-conditions", ["PII: privacy training not complete"]))

    def test_strictest_tier_wins_for_mixed_tags(self):
        r = review(with_(role="adjuster", tags=["PII", "GOV_ID"], days=30))
        self.assertEqual(r["decision"], "deny")  # adjuster may see PII but not GOV_ID
        self.assertTrue(any(x.startswith("GOV_ID: role") for x in r["reasons"]))

    def test_owner_approval_required_for_special_category(self):
        r = review(with_(role="siu_investigator", tags=["GOV_ID"], owner_approved=False))
        self.assertEqual((r["decision"], r["reasons"]), ("pending-conditions", ["GOV_ID: data owner approval needed"]))

    def test_duration_limit_and_blank_purpose_deny(self):
        self.assertEqual(review(with_(days=91))["decision"], "deny")
        self.assertEqual(review(with_(purpose="  "))["decision"], "deny")

    def test_unknown_role_denies_and_bad_input_raises(self):
        self.assertEqual(review(with_(role="intern", tags=[]))["decision"], "deny")
        with self.assertRaises(ValueError):
            review(with_(tags=["SECRET"]))
        with self.assertRaises(ValueError):
            review({k: v for k, v in BASE.items() if k != "days"})
        with self.assertRaises(ValueError):
            review(with_(days=0))


if __name__ == "__main__":
    unittest.main()
