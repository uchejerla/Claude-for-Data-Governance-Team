import pathlib
import unittest

from map_policy import DATA, coverage, priorities

ROOT = pathlib.Path(__file__).parent.parent.parent
ALL = set(DATA["controls"])


class PolicyMapperTest(unittest.TestCase):
    def status(self, have, **kw):
        return {r["id"]: r["status"] for r in coverage(have, **kw)}

    def test_nothing_implemented_is_all_gaps(self):
        self.assertEqual(set(self.status([]).values()), {"gap"})
        self.assertEqual(len(self.status([])), 12)

    def test_everything_implemented_is_all_covered(self):
        rows = coverage(ALL)
        self.assertEqual({r["status"] for r in rows}, {"covered"})
        self.assertEqual(priorities(rows), [])

    def test_partial_and_gap(self):
        s = self.status(["C-01"])
        self.assertEqual((s["R01"], s["R07"], s["R10"]), ("partial", "partial", "partial"))
        self.assertEqual((s["R04"], s["R02"]), ("gap", "gap"))

    def test_priorities_rank_by_requirements_blocked(self):
        p = priorities(coverage([]))
        self.assertEqual(p[0], ("C-01", 3))
        self.assertEqual({c for c, n in p if n == 3}, {"C-01", "C-05", "C-11"})
        # once C-01 exists it must drop out of the list
        self.assertNotIn("C-01", [c for c, _ in priorities(coverage(["C-01"]))])

    def test_source_filter(self):
        self.assertEqual(len(coverage([], sources=["GDPR"])), 5)

    def test_bad_input_rejected(self):
        with self.assertRaises(ValueError):
            coverage(["C-99"])
        with self.assertRaises(ValueError):
            coverage([], sources=["HIPAA"])

    def test_data_is_consistent(self):
        for r in DATA["requirements"]:
            self.assertIn(r["source"], DATA["sources"])
            self.assertTrue(set(r["controls"]) <= ALL, r["id"])
        for c in DATA["controls"].values():
            if c["kit"]:
                self.assertTrue((ROOT / c["kit"]).exists(), c["kit"])


if __name__ == "__main__":
    unittest.main()
