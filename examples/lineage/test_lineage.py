import json
import pathlib
import unittest

from explain_lineage import explain, impact, walk

G = json.loads((pathlib.Path(__file__).parent / "lineage_sample.json").read_text())


class LineageTest(unittest.TestCase):
    def test_downstream_distances(self):
        self.assertEqual(walk(G, "raw.claims"), {
            "stg.claims": 1, "dw.claim_header": 2, "dw.claim_payment": 2, "rpt.schedule_p": 3,
            "rpt.fast_track": 3, "rpt.market_conduct": 3, "dash.reserve_trend": 3})

    def test_upstream_distances(self):
        self.assertEqual(walk(G, "rpt.schedule_p", "up"), {
            "dw.claim_header": 1, "dw.claim_payment": 1, "stg.claims": 2, "dw.policy": 2,
            "raw.claims": 3, "src.policy_admin": 3, "src.claims_tpa": 4})

    def test_regulatory_reports_are_flagged(self):
        reg = {r["asset"] for r in impact(G, "stg.claims") if r.get("regulatory")}
        self.assertEqual(reg, {"rpt.schedule_p", "rpt.fast_track", "rpt.market_conduct"})
        self.assertTrue(explain(G, "stg.claims").endswith(
            "Regulatory reports affected: rpt.fast_track, rpt.market_conduct, rpt.schedule_p"))
        self.assertTrue(explain(G, "dw.claim_payment").endswith("Regulatory reports affected: rpt.schedule_p"))

    def test_leaf_has_no_downstream_and_a_source_has_no_upstream(self):
        self.assertEqual(walk(G, "rpt.schedule_p"), {})
        self.assertEqual(walk(G, "src.claims_tpa", "up"), {})

    def test_cycle_terminates(self):
        g = {"nodes": {"a": {"kind": "table"}, "b": {"kind": "table"}}, "edges": [["a", "b"], ["b", "a"]]}
        self.assertEqual(walk(g, "a"), {"b": 1})

    def test_bad_input_rejected(self):
        with self.assertRaises(ValueError):
            walk(G, "nope")
        with self.assertRaises(ValueError):
            walk({"nodes": {"a": {}}, "edges": [["a", "ghost"]]}, "a")
        with self.assertRaises(ValueError):
            walk(G, "raw.claims", "sideways")


if __name__ == "__main__":
    unittest.main()
