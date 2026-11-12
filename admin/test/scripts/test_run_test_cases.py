"""Tests for the pure logic in run_test_cases.py.

The artifact-execution path is exercised by the runner itself in CI; these
cover baseline selection, normalization, and the comparison verdicts against
synthetic inputs only.
"""
import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.append(os.path.dirname(__file__))

import run_test_cases as rtc  # noqa: E402  pylint: disable=wrong-import-position


class NormalizeRowsTests(unittest.TestCase):
    def test_temp_extract_path_is_tokenized(self):
        rows = [["admin/test/temp/extract_foo_bar_1750464339/x/y.plist", 1]]
        other = [["admin/test/temp/extract_foo_bar_1999999999/x/y.plist", 1]]
        self.assertEqual(rtc.normalize_rows(rows), rtc.normalize_rows(other))

    def test_row_order_does_not_matter(self):
        self.assertEqual(rtc.normalize_rows([[1, "a"], [2, "b"]]),
                         rtc.normalize_rows([[2, "b"], [1, "a"]]))

    def test_content_change_is_detected(self):
        self.assertNotEqual(rtc.normalize_rows([[1, "a"]]),
                            rtc.normalize_rows([[1, "b"]]))

    def test_tuple_and_list_rows_normalize_alike(self):
        self.assertEqual(rtc.normalize_rows([(1, "a")]), rtc.normalize_rows([[1, "a"]]))

    def test_windows_separators_compare_as_forward_slashes(self):
        windows = [["data\\data\\pkg\\db", 'say \\"hi\\"']]
        recorded = [["data/data/pkg/db", 'say /"hi/"']]
        self.assertEqual(rtc.normalize_rows(windows, backslash_paths=True),
                         rtc.normalize_rows(recorded, backslash_paths=True))

    def test_separators_are_kept_off_windows(self):
        self.assertNotEqual(rtc.normalize_rows([["data\\data"]], backslash_paths=False),
                            rtc.normalize_rows([["data/data"]], backslash_paths=False))

    def test_other_escapes_survive_separator_normalization(self):
        rows = [['a "quote"\nline\ttab']]
        self.assertEqual(rtc.normalize_rows(rows, backslash_paths=True),
                         rtc.normalize_rows(rows, backslash_paths=False))


class CompareTests(unittest.TestCase):
    BASE = {"headers": ["A", "B"], "data": [[1, "x"], [2, "y"]]}

    def test_match_returns_no_problems(self):
        self.assertEqual(rtc.compare(["A", "B"], [[2, "y"], [1, "x"]], self.BASE), [])

    def test_header_change_reported(self):
        problems = rtc.compare(["A", "C"], [[1, "x"], [2, "y"]], self.BASE)
        self.assertTrue(any("headers differ" in p for p in problems))

    def test_row_change_reported_with_counts(self):
        problems = rtc.compare(["A", "B"], [[1, "x"], [2, "z"]], self.BASE)
        joined = "\n".join(problems)
        self.assertIn("rows differ", joined)
        self.assertIn("1 new", joined)
        self.assertIn("1 missing", joined)


class LatestBaselineTests(unittest.TestCase):
    def test_picks_newest_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            mod_dir = Path(tmp) / "results" / "m"
            mod_dir.mkdir(parents=True)
            for stamp in ("20240101000000", "20250101000000", "20230101000000"):
                (mod_dir / f"m.a.case1.{stamp}.json").write_text("{}", encoding="utf-8")
            (mod_dir / "m.a.case2.20990101000000.json").write_text("{}", encoding="utf-8")
            old_results = rtc.RESULTS_DIR
            rtc.RESULTS_DIR = Path(tmp) / "results"
            try:
                chosen = rtc.latest_baseline("m", "a", "case1")
            finally:
                rtc.RESULTS_DIR = old_results
            self.assertEqual(chosen.name, "m.a.case1.20250101000000.json")

    def test_none_when_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_results = rtc.RESULTS_DIR
            rtc.RESULTS_DIR = Path(tmp)
            try:
                self.assertIsNone(rtc.latest_baseline("m", "a", "c"))
            finally:
                rtc.RESULTS_DIR = old_results


class BaselineJsonRoundTripTests(unittest.TestCase):
    def test_fresh_python_values_match_their_json_serialized_form(self):
        from datetime import datetime, timezone
        ts = int(datetime(2024, 5, 1, tzinfo=timezone.utc).timestamp())
        fresh = [[ts, b"bytes-value"]]
        recorded = json.loads(json.dumps({"data": fresh}, default=str))["data"]
        self.assertEqual(rtc.normalize_rows(fresh), rtc.normalize_rows(recorded))


class FreeUserIdTests(unittest.TestCase):
    def test_default_is_user_10(self):
        names = ["Dump/data/data/pkg/databases/a.db", "Dump/data/user/0/pkg/databases/a.db"]
        self.assertEqual(rtc.free_user_id(names), 10)

    def test_skips_users_the_fixture_already_holds(self):
        names = ["test_data/data/data/pkg/databases/a.db",
                 "test_data/data/user/10/pkg/databases/a.db",
                 "test_data/data/user_de/11/pkg/files/b",
                 "test_data/data/media/12/Download/c.jpg"]
        self.assertEqual(rtc.free_user_id(names), 13)

    def test_user_id_must_be_a_whole_path_segment(self):
        names = ["Dump/data/user/100/pkg/a.db", "Dump/notdata/user/10/pkg/a.db"]
        self.assertEqual(rtc.free_user_id(names), 10)


class TenantVariantTests(unittest.TestCase):
    def variant_names(self, names):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp) / "src.zip", Path(tmp) / "dst.zip"
            with zipfile.ZipFile(src, "w") as zout:
                for name in names:
                    zout.writestr(name, name)
            added, mapping = rtc.make_tenant_variant(src, dst)
            with zipfile.ZipFile(dst) as zin:
                return added, mapping, zin.namelist(), {n: zin.read(n) for n in zin.namelist()}

    def test_single_user_fixture_gets_user_10(self):
        added, mapping, names, _ = self.variant_names(
            ["Dump/data/data/pkg/databases/a.db"])
        self.assertEqual(mapping, {0: 10})
        self.assertEqual(added, 1)
        self.assertIn("Dump/data/user/10/pkg/databases/a.db", names)

    def test_every_app_data_user_is_copied_to_a_free_id(self):
        src = ["t/data/data/pkg/databases/a.db",
               "t/data/user/0/pkg/databases/a.db",
               "t/data/user/10/pkg/databases/a.db",
               "t/data/media/11/Pictures/p.jpg",
               "t/system/build.prop"]
        added, mapping, names, payloads = self.variant_names(src)
        # 11 is taken under data/media, so the new ids are 12 and 13.
        self.assertEqual(mapping, {0: 12, 10: 13})
        self.assertEqual(added, 2)
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(payloads["t/data/user/12/pkg/databases/a.db"],
                         b"t/data/data/pkg/databases/a.db")
        self.assertEqual(payloads["t/data/user/13/pkg/databases/a.db"],
                         b"t/data/user/10/pkg/databases/a.db")
        self.assertEqual(sorted(set(names) - set(src)),
                         ["t/data/user/12/pkg/databases/a.db",
                          "t/data/user/13/pkg/databases/a.db"])

    def test_variant_members_keep_their_bytes(self):
        # A member written to the variant must not move the source's offsets.
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp) / "src.zip", Path(tmp) / "dst.zip"
            members = {"Dump/system/big.bin": bytes(range(256)) * 400,
                       "Dump/data/data/pkg/a.db": b"A" * 5000,
                       "Dump/data/user/10/pkg/a.db": b"B" * 7000}
            with zipfile.ZipFile(src, "w", zipfile.ZIP_STORED) as zout:
                zout.comment = b"x" * 64
                for name, payload in members.items():
                    zout.writestr(name, payload)
            # Leading bytes shift every source offset away from the variant's.
            src.write_bytes(b"\0" * 4096 + src.read_bytes())
            rtc.make_tenant_variant(src, dst)
            with zipfile.ZipFile(dst) as zin:
                self.assertIsNone(zin.testzip())
                self.assertEqual(zin.read("Dump/data/user/11/pkg/a.db"), b"A" * 5000)
                self.assertEqual(zin.read("Dump/data/user/12/pkg/a.db"), b"B" * 7000)

    def test_nothing_per_user_adds_nothing(self):
        added, mapping, names, _ = self.variant_names(["Dump/system/build.prop"])
        self.assertEqual((added, mapping), (0, {}))
        self.assertEqual(names, ["Dump/system/build.prop"])


class CommitInfoTests(unittest.TestCase):
    def test_missing_git_records_unknown(self):
        from unittest import mock  # pylint: disable=import-outside-toplevel
        import test_module  # pylint: disable=import-outside-toplevel
        with mock.patch.object(test_module.subprocess, "check_output",
                               side_effect=FileNotFoundError("git")):
            info = test_module.get_last_commit_info("scripts/artifacts/x.py")
        self.assertEqual(info["hash"], "unknown")


if __name__ == "__main__":
    unittest.main()
