"""Regression tests for download/MediaStore correlation using synthetic databases."""

import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import chromeDownloadMediaStore as parser
from scripts.context import Context
from scripts import ilapfuncs, lavafuncs


class EvidenceContext:
    def __init__(self, root):
        self.root = root

    def get_files_found(self):
        return [str(path) for path in sorted(self.root.rglob("*")) if path.is_file()]

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def history(root, relative="data/user/0/org.example.browser/app_chrome/Default/History", **changes):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute("""CREATE TABLE downloads (
            id INTEGER PRIMARY KEY, guid TEXT, start_time INTEGER, end_time INTEGER,
            tab_url TEXT, referrer TEXT, current_path TEXT, target_path TEXT, state INTEGER,
            received_bytes INTEGER, total_bytes INTEGER, mime_type TEXT)""")
        db.execute("CREATE TABLE downloads_url_chains (id INTEGER, chain_index INTEGER, url TEXT)")
        row = dict(id=12, guid="00000000-0000-4000-8000-000000000012",
                   start_time=13369696675000000, end_time=13369696685000000,
                   tab_url="https://example.invalid/page", referrer="https://example.invalid/",
                   current_path="content://media/external/downloads/7001",
                   target_path="content://media/external/downloads/7001", state=1,
                   received_bytes=1234, total_bytes=1234, mime_type="image/jpeg")
        row.update(changes)
        db.execute("INSERT INTO downloads VALUES (" + ",".join("?" for _ in row) + ")", list(row.values()))
        db.execute("INSERT INTO downloads_url_chains VALUES (?,0,?)", (row["id"], "blob:https://example.invalid/fixture"))
    return path


def media(root, relative="data/user/0/com.google.android.providers.media.module/databases/external.db", **changes):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute("""CREATE TABLE files (
            _id INTEGER PRIMARY KEY, _data TEXT, _display_name TEXT, _size INTEGER,
            owner_package_name TEXT, mime_type TEXT, date_added INTEGER, date_modified INTEGER,
            volume_name TEXT, is_download INTEGER, is_pending INTEGER, is_trashed INTEGER)""")
        row = dict(_id=7001, _data="/storage/emulated/0/Download/fixture.jpg",
                   _display_name="fixture.jpg", _size=1234, owner_package_name="org.example.browser",
                   mime_type="image/jpeg", date_added=1725223075, date_modified=1725223085,
                   volume_name="external_primary", is_download=1, is_pending=0, is_trashed=0)
        row.update(changes)
        db.execute("INSERT INTO files VALUES (" + ",".join("?" for _ in row) + ")", list(row.values()))
    return path


class CorrelationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def parse(self):
        with patch.object(parser, "logfunc"):
            headers, rows, _ = parser.get_chromeDownloadMediaStore.__wrapped__(EvidenceContext(self.root))
        names = [header[0] if isinstance(header, tuple) else header for header in headers]
        return [dict(zip(names, row)) for row in rows]

    def test_resolves_media_id_instead_of_browser_id_or_guid(self):
        history(self.root)
        media(self.root)
        row, = self.parse()
        self.assertEqual(row["Download ID"], 12)
        self.assertEqual(row["MediaStore ID"], 7001)
        self.assertEqual(row["File Name"], "fixture.jpg")
        self.assertEqual(row["Correlation Status"], "MediaStore row found")
        self.assertEqual(row["Size Comparison"], "Matches received bytes")
        self.assertEqual(str(row["Start Time"]), "2024-09-01 20:37:55+00:00")
        self.assertNotIn(str(self.root), row["History DB Path"])
        self.assertIn("blob:", row["Download URL Chain"])

    def test_android_users_do_not_share_ids(self):
        history(self.root)
        media(self.root)
        history(self.root, "data/user/10/org.example.browser/app_chrome/Default/History")
        media(self.root, "data/user/10/com.google.android.providers.media.module/databases/external.db",
              _display_name="user10.jpg", _data="/storage/emulated/10/Download/user10.jpg")
        rows = {row["Android User ID"]: row for row in self.parse()}
        self.assertEqual(rows[0]["File Name"], "fixture.jpg")
        self.assertEqual(rows[10]["File Name"], "user10.jpg")

    def test_different_evidence_roots_do_not_share_ids(self):
        history(self.root, "device_a/data/user/0/org.example.browser/app_chrome/Default/History")
        media(self.root, "device_b/data/user/0/com.google.android.providers.media.module/databases/external.db")
        row, = self.parse()
        self.assertEqual(row["File Name"], "")
        self.assertIn("database unavailable", row["Correlation Status"])

    def test_duplicate_storage_views_are_collapsed(self):
        original = history(self.root, "data/data/org.example.browser/app_chrome/Default/History")
        other = self.root / "data/user/0/org.example.browser/app_chrome/Default/History"
        other.parent.mkdir(parents=True)
        shutil.copyfile(original, other)
        original = media(self.root, "data/data/com.google.android.providers.media.module/databases/external.db")
        other = self.root / "data_mirror/data_ce/null/0/com.google.android.providers.media.module/databases/external.db"
        other.parent.mkdir(parents=True)
        shutil.copyfile(original, other)
        row, = self.parse()
        self.assertEqual(row["Candidate Count"], 1)

    def test_different_provider_databases_are_ambiguous(self):
        history(self.root)
        media(self.root)
        media(self.root, "data/user/0/com.android.providers.media/databases/external.db", _display_name="other.jpg")
        row, = self.parse()
        self.assertEqual(row["Correlation Status"], "Ambiguous MediaStore rows")
        self.assertEqual(row["Candidate Count"], 2)
        self.assertEqual(row["File Path"], "")

    def test_missing_row_is_retained(self):
        history(self.root)
        media(self.root, _id=7002)
        row, = self.parse()
        self.assertIn("row not found", row["Correlation Status"])
        self.assertEqual(row["MediaStore ID"], 7001)

    def test_missing_database_is_retained(self):
        history(self.root)
        row, = self.parse()
        self.assertIn("database unavailable", row["Correlation Status"])

    def test_unknown_android_user_is_not_guessed(self):
        history(self.root, "History")
        media(self.root)
        row, = self.parse()
        self.assertEqual(row["Correlation Status"], "Android user not determined from the History path")

    def test_explicit_uri_user_is_used(self):
        uri = "content://10@media/external/downloads/7001"
        history(self.root, current_path=uri, target_path=uri)
        media(self.root)
        media(self.root, "data/user/10/com.google.android.providers.media.module/databases/external.db",
              _display_name="explicit_user.jpg")
        row, = self.parse()
        self.assertEqual(row["Android User ID"], 0)
        self.assertEqual(row["MediaStore User ID"], 10)
        self.assertEqual(row["File Name"], "explicit_user.jpg")

    def test_different_current_and_target_uris_are_retained(self):
        history(self.root, current_path="content://media/external/downloads/7002")
        media(self.root)
        rows = self.parse()
        self.assertEqual(len(rows), 2)
        self.assertEqual({row["MediaStore ID"] for row in rows}, {7001, 7002})

    def test_named_volume_must_match(self):
        uri = "content://media/external_primary/downloads/7001"
        history(self.root, current_path=uri, target_path=uri)
        media(self.root, volume_name="1234-abcd")
        row, = self.parse()
        self.assertIn("row not found", row["Correlation Status"])

    def test_external_alias_accepts_removable_volume(self):
        history(self.root)
        media(self.root, volume_name="1234-abcd")
        row, = self.parse()
        self.assertEqual(row["Correlation Status"], "MediaStore row found")

    def test_legacy_minimal_schema_is_supported(self):
        history(self.root)
        path = self.root / "data/user/0/com.android.providers.media/databases/external.db"
        path.parent.mkdir(parents=True)
        with sqlite3.connect(path) as db:
            db.execute("CREATE TABLE files (_id INTEGER, _data TEXT, _display_name TEXT)")
            db.execute("INSERT INTO files VALUES (7001,'/sdcard/Download/legacy.jpg','legacy.jpg')")
        row, = self.parse()
        self.assertEqual(row["File Name"], "legacy.jpg")
        self.assertEqual(row["Size Comparison"], "Unavailable")

    def test_corrupt_media_database_does_not_stop_history(self):
        history(self.root)
        path = self.root / "data/user/0/com.android.providers.media/databases/external.db"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"not a SQLite database")
        row, = self.parse()
        self.assertIn("database unavailable", row["Correlation Status"])

    def test_size_mismatch_and_owner_mismatch_are_visible(self):
        history(self.root)
        media(self.root, _size=555, owner_package_name="org.example.other", is_pending=1, is_trashed=1)
        row, = self.parse()
        self.assertEqual(row["Size Comparison"], "Differs from received bytes")
        self.assertIn("owner package differs", row["Notes"])
        self.assertIn("Pending", row["Notes"])
        self.assertIn("Trashed", row["Notes"])

    def test_rollback_snapshots_are_not_live_candidates(self):
        history(self.root)
        media(self.root)
        media(self.root, "data/misc_ce/0/rollback/1/com.google.android.providers.media.module/databases/external.db")
        row, = self.parse()
        self.assertEqual(row["Candidate Count"], 1)

    def test_invalid_and_out_of_range_uris_are_retained(self):
        for value in ("", "/storage/emulated/0/Download/a.jpg",
                      "content://media/external/downloads/7001?query=1",
                      "content://media/external/downloads/999999999999999999999999",
                      "content://downloads/public_downloads/7001"):
            with self.subTest(uri=value):
                self.assertIsNone(parser._media_uri(value))  # pylint: disable=protected-access

    def test_download_without_media_uri_is_not_reported(self):
        path = "/storage/emulated/0/Download/a.jpg"
        history(self.root, current_path=path, target_path=path)
        history(self.root, "data/user/0/org.example.other/app_chrome/Default/History",
                current_path="", target_path="")
        media(self.root)
        self.assertEqual(self.parse(), [])

    def test_timestamp_columns_lead(self):
        history(self.root)
        media(self.root)
        row, = self.parse()
        self.assertEqual(list(row)[:4], ["Start Time", "End Time", "MediaStore Date Added",
                                         "MediaStore Date Modified"])
        self.assertEqual(str(row["MediaStore Date Added"]), "2024-09-01 20:37:55+00:00")

    def test_input_bytes_are_unchanged(self):
        files = [history(self.root), media(self.root)]
        before = [hashlib.sha256(path.read_bytes()).digest() for path in files]
        self.parse()
        self.assertEqual(before, [hashlib.sha256(path.read_bytes()).digest() for path in files])

    def test_uncheckpointed_mediastore_wal_is_read(self):
        history(self.root)
        path = media(self.root, _id=7002)
        db = sqlite3.connect(path)
        try:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA wal_autocheckpoint=0")
            db.execute("UPDATE files SET _id=7001, _display_name='wal.jpg'")
            db.commit()
            wal = Path(str(path) + "-wal")
            before = [hashlib.sha256(file.read_bytes()).digest() for file in (path, wal)]
            row, = self.parse()
            self.assertEqual(row["File Name"], "wal.jpg")
            self.assertEqual(before, [hashlib.sha256(file.read_bytes()).digest() for file in (path, wal)])
        finally:
            db.close()

    def test_decorated_artifact_writes_lava_timeline_and_reports(self):
        history(self.root)
        media(self.root)
        output = self.root / "output"
        # OutputParameters stores the log paths on the class, so put them back afterwards
        # or every later test logs into this test's removed folder.
        log_paths = (ilapfuncs.OutputParameters.screen_output_file_path,
                     ilapfuncs.OutputParameters.screen_output_file_path_devinfo)
        params = ilapfuncs.OutputParameters(str(output), "integration")
        Context.set_output_params(params)
        Context.set_data_folder(str(self.root))
        report = Path(params.output_folder_base) / "_HTML" / "Chromium"
        report.mkdir(parents=True)
        files = EvidenceContext(self.root).get_files_found()
        lavafuncs.initialize_lava(str(self.root), params.output_folder_base, "fs")
        try:
            _, rows, _ = parser.get_chromeDownloadMediaStore(  # pylint: disable=too-many-function-args
                files, str(report), object(), False)
            self.assertEqual(len(rows), 1)
            lavafuncs.lava_db.commit()
            tables = lavafuncs.lava_db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            artifact_tables = [name for name, in tables if "chromedownloadmediastore" in name]
            self.assertEqual(len(artifact_tables), 1)
            stored = lavafuncs.lava_db.execute('SELECT * FROM "' + artifact_tables[0] + '"').fetchall()
            self.assertEqual(len(stored), 1)
            self.assertIn("fixture.jpg", stored[0])
            with sqlite3.connect(Path(params.output_folder_base) / "_Timeline" / "tl.db") as db:
                timeline, = db.execute("SELECT datalist FROM data").fetchall()
                self.assertEqual(json.loads(timeline[0])["File Name"], "fixture.jpg")
            self.assertTrue(list(Path(params.output_folder_base).rglob("*.html")))
            self.assertTrue(list(Path(params.output_folder_base).rglob("*.tsv")))
        finally:
            lavafuncs.lava_db.close()
            lavafuncs.lava_db = None
            ilapfuncs.close_screen_log()
            (ilapfuncs.OutputParameters.screen_output_file_path,
             ilapfuncs.OutputParameters.screen_output_file_path_devinfo) = log_paths
            Context.clear()
            Context.set_output_params(None)
            Context.set_data_folder(None)


if __name__ == "__main__":
    unittest.main()
