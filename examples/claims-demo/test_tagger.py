import unittest

from generate_claims import generate
from tag_sensitivity import SAMPLE, tag_columns


class TaggerTest(unittest.TestCase):
    def test_expected_tags(self):
        got = tag_columns(SAMPLE)
        self.assertEqual(got["claimant_name"], ["PII"])
        self.assertEqual(got["claimant_ssn"], ["GOV_ID"])
        self.assertEqual(got["claimant_dob"], ["PII"])
        self.assertEqual(got["driver_license_no"], ["GOV_ID"])
        self.assertEqual(got["injury_description"], ["PHI"])
        self.assertEqual(got["icd10_code"], ["PHI"])
        self.assertEqual(got["bank_account_no"], ["FINANCIAL_ACCOUNT"])
        self.assertEqual(got["email_address"], ["PII"])

    def test_no_false_positives_on_business_columns(self):
        got = tag_columns(["claim_id", "policy_id", "loss_date", "claim_amount", "state", "product_name"])
        self.assertTrue(all(tags == [] for tags in got.values()))

    def test_camel_case(self):
        self.assertEqual(tag_columns(["claimantSSN", "FirstName"]), {"claimantSSN": ["GOV_ID"], "FirstName": ["PII"]})

    def test_demo_table_has_no_sensitive_columns(self):
        self.assertTrue(all(t == [] for t in tag_columns(generate()[0]).values()))


if __name__ == "__main__":
    unittest.main()
