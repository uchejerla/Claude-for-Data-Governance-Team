import json
import pathlib
import unittest

from identify_cdes import rank, score

CATALOG = json.loads((pathlib.Path(__file__).parent / "catalog_sample.json").read_text())


class CdeTest(unittest.TestCase):
    def decisions(self):
        return {r["column"]: r["decision"] for r in rank(CATALOG)}

    def test_sample_decisions(self):
        d = self.decisions()
        for c in ("paid_amount", "claim_id", "reserve_amount"):
            self.assertEqual(d[c], "CDE candidate", c)
        for c in ("loss_date", "report_date", "state", "policy_id", "claimant_ssn"):
            self.assertEqual(d[c], "steward review", c)
        for c in ("claim_status", "claimant_email"):
            self.assertEqual(d[c], "not a CDE", c)
        self.assertEqual(d["adjuster_notes"], "needs metadata")

    def test_exact_scores_and_order(self):
        scores = {r["column"]: r["score"] for r in rank(CATALOG)}
        self.assertEqual((scores["paid_amount"], scores["claim_id"], scores["reserve_amount"]), (8, 7, 7))
        self.assertEqual(rank(CATALOG)[0]["column"], "paid_amount")

    def test_missing_metadata_is_listed_not_guessed(self):
        r = score({"column": "adjuster_notes"})
        self.assertEqual(r["score"], 0)
        self.assertEqual(set(r["unknown"]), {"regulatory_reports", "financial_impact", "downstream_assets", "is_key", "sensitivity"})

    def test_every_decision_has_reasons_unless_zero(self):
        for r in rank(CATALOG):
            self.assertTrue(r["why"] or r["score"] == 0, r["column"])


if __name__ == "__main__":
    unittest.main()
