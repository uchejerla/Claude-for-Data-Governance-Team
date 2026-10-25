import json
import unittest

from generate_claims import INJECTED, generate
from run_dq import HERE, run

RULE_TO_DEFECT = {
    "CLM-001": "duplicate_claim_id", "CLM-002": "null_loss_date", "CLM-003": "report_before_loss",
    "CLM-004": "invalid_state", "CLM-005": "invalid_status", "CLM-006": "paid_exceeds_claim",
    "CLM-007": "late_report",
}


class DemoTest(unittest.TestCase):
    def setUp(self):
        self.rules = json.loads((HERE / "rules.json").read_text())

    def test_each_rule_finds_exactly_the_injected_defects(self):
        _, results = run(generate(), self.rules)
        self.assertEqual({r["id"] for r in results}, set(RULE_TO_DEFECT))
        for r in results:
            self.assertEqual(r["failed"], INJECTED[RULE_TO_DEFECT[r["id"]]], r["id"])

    def test_threshold_decides_pass_fail(self):
        _, results = run(generate(), self.rules)
        # 99% rules tolerate their few bad rows; the 100% rules do not
        self.assertEqual({r["id"] for r in results if r["pass"]}, {"CLM-004", "CLM-005"})

    def test_empty_rows_rejected(self):
        with self.assertRaises(ValueError):
            run([], self.rules)

    def test_non_select_rule_rejected(self):
        bad = [{"id": "X", "fail_sql": "ATTACH DATABASE 'x.db' AS x", "threshold": 1.0}]
        with self.assertRaises(ValueError):
            run(generate(), bad)

    def test_clean_data_passes_everything(self):
        rows = generate()
        clean = [r for i, r in enumerate(rows[:5])]  # first 5 rows are never mutated
        _, results = run(clean, self.rules)
        self.assertTrue(all(r["pass"] for r in results))

    def test_deterministic(self):
        self.assertEqual(generate(), generate())


if __name__ == "__main__":
    unittest.main()
