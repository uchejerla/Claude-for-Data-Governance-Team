import json
import pathlib
import tempfile
import unittest

from audit import head, log_event, read, verify
from mask import assert_no_leaks, find_leaks, mask_rows, scrub

KEY = "test-key-not-secret"
ROW = {"claim_id": "CLM1", "claimant_name": "Jane Roe", "claimant_ssn": "123-45-6789", "claimant_dob": "1980-02-03",
       "email_address": "jane@example.com", "adjuster_notes": "Called Jane at 555-123-4567, card 4111 1111 1111 1111",
       "reference": "SSN on file 987-65-4321", "claim_amount": 1200.5, "state": "TX", "loss_date": None}
RAW_VALUES = ["Jane Roe", "123-45-6789", "1980-02-03", "jane@example.com", "555-123-4567", "4111", "987-65-4321"]


class MaskTest(unittest.TestCase):
    def test_sensitive_columns_become_stable_keyed_tokens(self):
        (m,), report = mask_rows([ROW], KEY)
        self.assertRegex(m["claimant_ssn"], r"^GOV_ID:[0-9a-f]{10}$")
        self.assertRegex(m["claimant_name"], r"^PII:[0-9a-f]{10}$")
        (again,), _ = mask_rows([ROW], KEY)
        (other,), _ = mask_rows([ROW], "a-different-key")
        self.assertEqual(m, again)
        self.assertNotEqual(m["claimant_ssn"], other["claimant_ssn"])

    def test_same_value_gets_same_token_so_joins_still_work(self):
        rows, _ = mask_rows([ROW, {**ROW, "claim_id": "CLM2"}], KEY)
        self.assertEqual(rows[0]["claimant_ssn"], rows[1]["claimant_ssn"])

    def test_no_raw_value_survives_in_rows_or_report(self):
        rows, report = mask_rows([ROW], KEY)
        text = json.dumps([rows, report])
        for raw in RAW_VALUES:
            self.assertNotIn(raw, text)
        assert_no_leaks(rows)

    def test_free_text_redacted_by_default_untagged_cells_scrubbed_business_data_kept(self):
        (m,), report = mask_rows([ROW], KEY)
        self.assertEqual(m["adjuster_notes"], "[REDACTED_FREE_TEXT]")
        self.assertEqual(m["reference"], "SSN on file [SSN]")  # untagged column, caught by pattern
        self.assertEqual((m["claim_amount"], m["state"], m["loss_date"], m["claim_id"]), (1200.5, "TX", None, "CLM1"))
        self.assertEqual(report["redacted"], {"adjuster_notes": 1})
        self.assertEqual(report["scrubbed"], {"reference": 1})

    def test_scrub_free_text_option_and_its_documented_limit(self):
        (m,), _ = mask_rows([ROW], KEY, scrub_free_text=True)
        self.assertEqual(m["adjuster_notes"], "Called Jane at [PHONE], card [CARD]")
        self.assertIn("Jane", m["adjuster_notes"])  # limit: names in free text are not detected

    def test_card_needs_a_valid_checksum(self):
        self.assertEqual(scrub("pay 4111 1111 1111 1111 now"), "pay [CARD] now")
        self.assertEqual(scrub("order 1234 5678 9012 3456"), "order 1234 5678 9012 3456")  # fails Luhn

    def test_gate_catches_raw_data_without_echoing_it(self):
        with self.assertRaises(ValueError) as cm:
            assert_no_leaks([ROW])
        msg = str(cm.exception)
        self.assertIn("claimant_ssn", msg)
        self.assertNotIn("123-45-6789", msg)
        self.assertEqual(sorted(find_leaks("a@b.co 123-45-6789")), ["EMAIL", "SSN"])

    def test_key_required(self):
        with self.assertRaises(ValueError):
            mask_rows([ROW], "")


class AuditTest(unittest.TestCase):
    def setUp(self):
        self.path = pathlib.Path(tempfile.mkdtemp()) / "audit.jsonl"
        self.rec = log_event(self.path, "recommendation", now="2026-10-25T10:00:00+00:00", requester="R4 (example)",
                             skill="access-request-reviewer", skill_version="0.1", input_ref="requests_sample.json#R4",
                             output_sha256="ab" * 32, recommendation="deny")
        log_event(self.path, "decision", now="2026-10-25T11:00:00+00:00", ref=1, approver="R. Gomez (example)", decision="rejected")

    def test_intact_log_verifies_and_links_decision_to_recommendation(self):
        self.assertEqual(verify(self.path), [])
        recs = read(self.path)
        self.assertEqual((recs[0]["prev_hash"], recs[1]["prev_hash"]), ("0" * 64, recs[0]["hash"]))
        self.assertEqual(head(self.path)["count"], 2)

    def _lines(self):
        return self.path.read_text().splitlines()

    def test_edit_is_detected(self):
        self.path.write_text("\n".join(self._lines()).replace('"deny"', '"approve"') + "\n")
        self.assertIn("record 1: contents changed after writing", verify(self.path))

    def test_deleted_record_is_detected(self):
        log_event(self.path, "decision", ref=1, approver="A. Patel (example)", decision="deferred")
        first, _, third = self._lines()
        self.path.write_text(first + "\n" + third + "\n")
        self.assertTrue(verify(self.path))

    def test_reordering_is_detected(self):
        a, b = self._lines()
        self.path.write_text(b + "\n" + a + "\n")
        self.assertTrue(verify(self.path))

    def test_tail_truncation_needs_a_stored_head(self):
        before = head(self.path)
        self.path.write_text(self._lines()[0] + "\n")
        self.assertEqual(verify(self.path), [])  # limit: chain still valid
        self.assertNotEqual(head(self.path), before)  # but the stored head exposes it

    def test_sensitive_data_cannot_be_logged(self):
        with self.assertRaises(ValueError):
            log_event(self.path, "recommendation", requester="x", skill="s", skill_version="1", input_ref="ssn 123-45-6789",
                      output_sha256="a", recommendation="deny")
        self.assertEqual(len(read(self.path)), 2)

    def test_hash_with_card_like_digit_run_is_accepted_but_malformed_hash_is_not(self):
        base = dict(requester="x", skill="s", skill_version="1", input_ref="r", recommendation="deny")
        log_event(self.path, "recommendation", output_sha256="4111111111111111" + "ab" * 24, **base)
        with self.assertRaises(ValueError):
            log_event(self.path, "recommendation", output_sha256="not-a-hash", **base)

    def test_decision_rules(self):
        base = dict(ref=1, decision="approved")
        for bad in (dict(base, approver="Claude"), dict(base, approver=" "), dict(ref=9, approver="A. Patel", decision="approved"),
                    dict(ref=2, approver="A. Patel", decision="approved"), dict(ref=1, approver="A. Patel", decision="maybe")):
            with self.assertRaises(ValueError, msg=bad):
                log_event(self.path, "decision", **bad)
        self.assertEqual(len(read(self.path)), 2)

    def test_missing_or_unexpected_fields_rejected(self):
        with self.assertRaises(ValueError):
            log_event(self.path, "recommendation", requester="x")
        with self.assertRaises(ValueError):
            log_event(self.path, "decision", ref=1, approver="A. Patel", decision="approved", raw_data="x")


if __name__ == "__main__":
    unittest.main()
