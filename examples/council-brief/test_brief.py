import copy
import json
import pathlib
import unittest

from make_brief import brief, change, flags

M = json.loads((pathlib.Path(__file__).parent / "metrics_sample.json").read_text())


class BriefTest(unittest.TestCase):
    def test_flags_for_sample(self):
        self.assertEqual(flags(M), [
            "5 of 7 DQ rules are below target",
            "DQ-12 Duplicate claim IDs (critical) is 9 days old, SLA is 7",
            "DQ-15 Paid amount above claim amount (high) is 20 days old, SLA is 14",
            "CDEs with an active DQ rule (%) is 66.7%, target is 80%",
        ])

    def test_changes_versus_prior(self):
        text = brief(M)
        self.assertIn("| DQ overall score (%) | 98.8 | 98.1 | +0.7 |", text)
        self.assertIn("| CDEs with an owner (%) | 100.0 | 66.7 | +33.3 |", text)
        self.assertIn("| Access requests pending | 4 | 2 | +2 |", text)
        # 2/3 vs 1/3 is a 33.3 point rise; subtracting the rounded 66.7 - 33.3 would wrongly show +33.4
        self.assertIn("| CDEs with an active DQ rule (%) | 66.7 | 33.3 | +33.3 |", text)

    def test_decisions_come_only_from_input(self):
        text = brief(M)
        self.assertIn("1. Name an owner for claim header data", text)
        m = copy.deepcopy(M)
        m["decisions"] = []
        self.assertIn("None this month", brief(m))

    def test_clean_month_has_no_flags(self):
        m = copy.deepcopy(M)
        m["current"].update(rules_passing=7, cde_with_dq_rule=3)
        m["open_issues"] = []
        self.assertEqual(flags(m), [])
        self.assertIn("- Nothing flagged", brief(m))

    def test_no_prior_period_shows_na_and_zero_cdes_does_not_crash(self):
        m = copy.deepcopy(M)
        del m["prior"]
        m["current"].update(cde_total=0, cde_with_owner=0, cde_with_dq_rule=0)
        text = brief(m)
        self.assertIn("| DQ overall score (%) | 98.8 | n/a | n/a |", text)
        self.assertIn("| CDEs with an owner (%) | n/a | n/a | n/a |", text)

    def test_unknown_severity_raises(self):
        m = copy.deepcopy(M)
        m["open_issues"].append({"id": "X", "title": "t", "severity": "urgent", "age_days": 1})
        with self.assertRaises(ValueError):
            flags(m)

    def test_change_helper(self):
        self.assertEqual((change(3, 1), change(1, 3), change(None, 1)), ("+2", "-2", "n/a"))


if __name__ == "__main__":
    unittest.main()
