import unittest

from run_demo import build

R = build()


class EndToEndTest(unittest.TestCase):
    def test_all_eight_sections_present(self):
        for n in range(1, 9):
            self.assertIn(f"## {n}. ", R)

    def test_live_numbers_flow_through(self):
        self.assertIn("2/7 rules passing", R)
        self.assertIn("| DQ rules passing | 2 | 1 | +1 |", R)
        self.assertIn("| DQ overall score (%) | 98.8 | 98.1 | +0.7 |", R)
        self.assertIn("| CDEs with an active DQ rule (%) | 66.7 | 33.3 | +33.3 |", R)

    def test_cde_rule_coverage_gap_is_visible(self):
        self.assertIn("| reserve_amount | 7 | none yet |", R)
        self.assertIn("| paid_amount | 8 | yes |", R)

    def test_tags_lineage_access_policy_glossary(self):
        self.assertIn("| claimant_ssn | GOV_ID |", R)
        self.assertIn("regulatory reports affected: rpt.fast_track, rpt.market_conduct, rpt.schedule_p", R)
        self.assertIn("R4 (example) -> dw.claimant: **deny**", R)
        self.assertIn("Controls the kit evidences today: C-01, C-02, C-04", R)
        self.assertIn("Open Claim: **ready-for-review**", R)
        self.assertIn("Active Customer: **not-publishable**", R)

    def test_deterministic(self):
        self.assertEqual(R, build())


if __name__ == "__main__":
    unittest.main()
