"""Metadata attribution, browser-reference boundaries and resource-level events."""

from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import struct
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from admin.test.scripts.test_chrome_cache_videos import fixture, PUBLIC_CASE_ZIP
from admin.test.scripts.test_snss_parser import _file, _navigation
from scripts import chrome_cache_context as cc
from scripts import chrome_cache_video as cv
from scripts.artifacts import chromeCacheVideos as artifact

BASE_TIME = 13344473600000000
MEDIA_URL = "https://v.redd.it/synthetic/DASH_96.mp4"
POST_URL = "https://www.reddit.com/r/example/comments/test123/media/"
PAGE_URL = "https://www.reddit.com/r/example/comments/page123/context/"
PREFIX = "Dump/data/data/com.android.chrome/"


def pickle_payload(body):
    return struct.pack("<I", len(body)) + body


def response_info(request=BASE_TIME, response=BASE_TIME + 1000):
    headers = b"HTTP/1.1 206 Partial Content\x00Content-Type: video/mp4\x00Date: Wed, 01 Jan 2020 00:00:00 GMT\x00Last-Modified: Tue, 01 Jan 2019 00:00:00 GMT\x00Content-Range: bytes 0-999/1000\x00"
    body = struct.pack("<IqqI", 3, request, response, len(headers)) + headers
    return pickle_payload(body + b"\0" * (-len(body) % 4))


def cache_entry(body, key, metadata=None):
    raw = key.encode()
    metadata = response_info() if metadata is None else metadata
    return (struct.pack("<QIIII", cv.INITIAL_MAGIC, 9, len(raw), 0, 0) + raw + body
            + struct.pack("<QIIII", cv.FINAL_MAGIC, 0, 0, 0, 0) + metadata
            + hashlib.sha256(raw).digest()
            + struct.pack("<QIIII", cv.FINAL_MAGIC, 2, 0, len(metadata), 0))


def index_file(hashes):
    body = struct.pack("<QIQQI", cc.INDEX_MAGIC, 9, len(hashes), 10000, 0)
    body += b"".join(struct.pack("<QqQ", int(value, 16), BASE_TIME + 2000 + number, 256 << 8)
                     for number, value in enumerate(hashes))
    body += struct.pack("<q", BASE_TIME + 9999)
    return struct.pack("<II", len(body), 0) + body


def stage_context(root):
    """Entirely synthetic known content, including browser DBs and SNSS."""
    app = root / PREFIX
    cache = app / "cache/Cache_Data"
    cache.mkdir(parents=True)
    parts, _ = fixture()
    for number, part in enumerate(parts):
        (cache / f"{number:016x}_0").write_bytes(cache_entry(part, MEDIA_URL))
    index = cache / "index-dir/the-real-index"
    index.parent.mkdir()
    index.write_bytes(index_file([f"{number:016x}" for number in range(4)]))
    feed_url = "https://www.reddit.com/r/example/top.json?source_post_id=t3_page123"
    post = {"id": "test123", "title": "Synthetic preview", "permalink": "/r/example/comments/test123/media/",
            "promoted": True, "secure_media": {"reddit_video": {"scrubber_media_url": MEDIA_URL}}}
    (cache / "feed_0").write_bytes(cache_entry(gzip.compress(json.dumps({"data": [post]}).encode(), mtime=0), feed_url))
    profile = app / "app_chrome/Default"
    profile.mkdir(parents=True)
    with sqlite3.connect(profile / "History") as db:
        db.executescript("CREATE TABLE urls(id INTEGER PRIMARY KEY,url TEXT,title TEXT); CREATE TABLE visits(id INTEGER PRIMARY KEY,url INTEGER,visit_time INTEGER,from_visit INTEGER,transition INTEGER);")
        for number, url in enumerate((PAGE_URL, POST_URL, "https://unrelated.invalid/"), 1):
            db.execute("INSERT INTO urls VALUES(?,?,?)", (number, url, "Synthetic page"))
            db.execute("INSERT INTO visits VALUES(?,?,?,?,?)", (number, number, BASE_TIME - number, 0, 1))
    with sqlite3.connect(profile / "Media History") as db:
        db.executescript("CREATE TABLE playback(id INTEGER PRIMARY KEY,url TEXT,last_updated_time_s INTEGER,watch_time_s INTEGER,has_video INTEGER,has_audio INTEGER); CREATE TABLE playbackSession(id INTEGER PRIMARY KEY,url TEXT,last_updated_time_s INTEGER,title TEXT,position_ms INTEGER,duration_ms INTEGER);")
        db.execute("INSERT INTO playback VALUES(1,?,?,12,1,0)", (MEDIA_URL, BASE_TIME // 1000000))
        db.execute("INSERT INTO playbackSession VALUES(1,?,?,?,100,200)", (POST_URL, BASE_TIME // 1000000, "Synthetic session"))
    sessions = profile / "Sessions"
    sessions.mkdir()
    (sessions / "Tabs_100").write_bytes(_file((1, _navigation(url=PAGE_URL, timestamp=BASE_TIME - 100))))
    return [(path, path.relative_to(root).as_posix()) for path in sorted(root.rglob("*")) if path.is_file()]


class FileContext:
    def __init__(self, root, inputs, report):
        self.root, self.inputs, self.report = root, inputs, report

    def get_files_found(self):
        return [str(path) for path, _ in self.inputs]

    def get_relative_path(self, path):
        return Path(path).relative_to(self.root).as_posix()

    def get_report_folder(self):
        self.report.mkdir(parents=True, exist_ok=True)
        return str(self.report)


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "input"
        self.inputs = stage_context(self.source)
        self.output, self.manifest = cv.recover_files(
            [(path, relative) for path, relative in self.inputs if cc.cache_input(relative)], self.root / "output")
        self.assertEqual(len(self.manifest["clips"]), 1)

    def context(self, inputs=None):
        with patch.object(cc, "open_sqlite_db_readonly", side_effect=lambda path: sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)):
            return cc.build_context(self.inputs if inputs is None else inputs, self.manifest)

    def test_dates_exact_reference_and_server_dates_remain_strings(self):
        result = self.context()
        resource = next(iter(result["resources"].values()))
        self.assertEqual(len(resource["metadata"]), 4)
        self.assertEqual(resource["metadata"][0]["request_time"], cc.chrome_time(BASE_TIME))
        self.assertEqual(resource["metadata"][0]["last_used"], cc.chrome_time(BASE_TIME + 2000))
        self.assertEqual(len(resource["posts"]), 1)
        self.assertTrue(resource["posts"][0]["promoted"])
        self.assertEqual(resource["posts"][0]["role"], "Scrubber preview")
        self.assertIsInstance(resource["metadata"][0]["headers"]["last-modified"][0], str)
        self.assertEqual(Counter(event["kind"] for event in cc.resource_events(result)),
                         {"HTTP request time": 4, "HTTP response time": 4, "Cache last used": 4,
                          "History visit": 2, "Session navigation": 1, "Media History playback": 1, "Media History session": 1})
        self.assertEqual(len(resource["activities"]), 5)
        self.assertEqual(result["diagnostics"]["history_records_read"], 3)
        self.assertTrue(all(not event["kind"].startswith("Video watched") for event in cc.resource_events(result)))

    def test_time_proximity_without_url_relationship_does_not_join(self):
        history = next(path for path, _ in self.inputs if path.name == "History")
        with sqlite3.connect(history) as db:
            db.execute("UPDATE urls SET url='https://www.reddit.com/r/example/comments/other1/unrelated/'")
        result = self.context()
        resource = next(iter(result["resources"].values()))
        self.assertFalse(any(a["kind"] == "History visit" for a in resource["activities"]))

    def test_multiple_profiles_withhold_browser_joins(self):
        history = next(path for path, _ in self.inputs if path.name == "History")
        other = history.parent.parent / "Profile 1/History"
        other.parent.mkdir()
        shutil.copyfile(history, other)
        result = self.context(self.inputs + [(other, other.relative_to(self.source).as_posix())])
        resource = next(iter(result["resources"].values()))
        self.assertEqual(resource["profile_candidates"], ["Default", "Profile 1"])
        self.assertFalse(resource["activities"])
        self.assertEqual(len(resource["posts"]), 1)

    def test_oversize_profile_does_not_silently_remove_profile_ambiguity(self):
        history = next(path for path, _ in self.inputs if path.name == "History")
        other = history.parent.parent / "Profile 1/History"
        other.parent.mkdir()
        other.write_bytes(b"0" * 200000)
        with patch.object(cc, "MAX_CONTEXT_INPUT", 100000):
            result = self.context(self.inputs + [(other, other.relative_to(self.source).as_posix())])
        resource = next(iter(result["resources"].values()))
        self.assertEqual(resource["profile_candidates"], ["Default", "Profile 1"])
        self.assertFalse(resource["activities"])
        self.assertEqual(result["diagnostics"]["oversized_context_inputs_skipped"], 1)

    def test_other_user_storage_and_evidence_root_do_not_join(self):
        ancillary = [(path, relative) for path, relative in self.inputs if "/app_chrome/" in relative or path.name == "feed_0"]
        base = [(path, relative) for path, relative in self.inputs if (path, relative) not in ancillary]
        for replacement in ("OtherDump/data/data", "Dump/data/user/10", "Dump/data/user_de/0"):
            with self.subTest(replacement=replacement):
                result = self.context(base + [(path, relative.replace("Dump/data/data", replacement)) for path, relative in ancillary])
                resource = next(iter(result["resources"].values()))
                self.assertFalse(resource["activities"])
                self.assertFalse(resource["posts"])

    def test_unknown_index_does_not_discard_valid_http_dates(self):
        index = next(path for path, _ in self.inputs if path.name == "the-real-index")
        body = bytearray(index.read_bytes())
        struct.pack_into("<I", body, 16, 999)
        index.write_bytes(body)
        resource = next(iter(self.context()["resources"].values()))
        self.assertEqual(len(resource["metadata"]), 4)
        self.assertTrue(resource["metadata"][0]["response_time"])
        self.assertFalse(resource["metadata"][0]["last_used"])

    def test_wrong_sparse_sibling_key_is_rejected(self):
        # Use a real entry hash to exercise the sibling path, not a missing-file case.
        cache = next(path.parent for path, _ in self.inputs if path.name == "0000000000000000_0")
        path = cache / "0000000000000000_s"
        key = b"https://v.redd.it/different/DASH_96.mp4"
        path.write_bytes(struct.pack("<QIIII", cv.INITIAL_MAGIC, 9, len(key), 0, 0) + key)
        manifest = {"sources": {"s": {"path": path.relative_to(self.source).as_posix(), "url": key.decode()}},
                    "clips": [{"source": "s", "sha256": "synthetic"}]}
        with patch.object(cc, "open_sqlite_db_readonly", return_value=None):
            result = cc.build_context(self.inputs + [(path, path.relative_to(self.source).as_posix())], manifest)
        self.assertEqual(result["diagnostics"]["metadata_cache_key_mismatch"], 1)
        self.assertFalse(next(iter(result["resources"].values()))["metadata"])

    def test_invalid_key_digest_and_gzip_bomb_are_rejected(self):
        path = self.root / "bad_0"
        body = bytearray(cache_entry(b"", MEDIA_URL))
        body[-25] ^= 1
        path.write_bytes(body)
        with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
            cc.entry_metadata(path)
        path.write_bytes(cache_entry(gzip.compress(b"[" + b" " * 2048 + b"]"), "https://www.reddit.com/top.json"))
        with patch.object(cc, "MAX_JSON", 1024), self.assertRaises(ValueError):
            list(cc._json_bodies(path))  # pylint: disable=protected-access

    def test_missing_metadata_retains_recovered_resource_without_events(self):
        result = self.context([(p, r) for p, r in self.inputs if p.name.endswith("_0") and p.name != "feed_0"])
        resource = next(iter(result["resources"].values()))
        self.assertFalse(resource["posts"])
        self.assertFalse(resource["activities"])
        self.assertEqual(len(cc.resource_events(result)), 8)
        # Absent/unreadable stream-0 metadata is not replaced by a file mtime.
        for path, _ in self.inputs:
            if path.name.endswith("_0"):
                payload = bytearray(path.read_bytes())
                length = struct.unpack_from("<I", payload, len(payload) - 8)[0]
                struct.pack_into("<I", payload, len(payload) - 24 - 32 - length + 4, 0)
                path.write_bytes(payload)
        for source in self.manifest["sources"].values():
            source["sha256"] = cv.file_hash(self.source / source["path"])
        result = self.context([(p, r) for p, r in self.inputs if p.name.endswith("_0") and p.name != "feed_0"])
        self.assertFalse(cc.resource_events(result))

    def test_other_cache_directory_and_partition_do_not_join_posts(self):
        changed = [(path, relative.replace("cache/Cache_Data/feed_0", "cache/Other/feed_0") if path.name == "feed_0" else relative)
                   for path, relative in self.inputs]
        self.assertFalse(next(iter(self.context(changed)["resources"].values()))["posts"])
        path = next(path for path, _ in self.inputs if path.name == "feed_0")
        body = path.read_bytes()
        key, spans, _ = cv.cache_spans(body)
        path.write_bytes(cache_entry(body[spans[0].start:spans[0].end], "1/0/_dk_https://other.invalid " + key))
        self.assertFalse(next(iter(self.context()["resources"].values()))["posts"])

    def test_different_rendition_or_query_token_does_not_match(self):
        path = next(path for path, _ in self.inputs if path.name == "feed_0")
        key, spans, _ = cv.cache_spans(path.read_bytes())
        original = gzip.decompress(path.read_bytes()[spans[0].start:spans[0].end])
        for replacement in (MEDIA_URL.replace("96", "720"), MEDIA_URL + "?token=other", MEDIA_URL + "/"):
            with self.subTest(replacement=replacement):
                path.write_bytes(cache_entry(original.replace(MEDIA_URL.encode(), replacement.encode()), key))
                self.assertFalse(next(iter(self.context()["resources"].values()))["posts"])

    def test_multiple_clips_share_source_events(self):
        self.manifest["clips"].append(dict(self.manifest["clips"][0], sha256="second-clip"))
        events = cc.resource_events(self.context())
        self.assertEqual(len(events), 17)
        self.assertTrue(all(len(event["clip_hashes"]) == 2 for event in events))

    def test_empty_and_out_of_range_dates_stay_empty(self):
        for value in (None, "", 0, -1, "invalid", 10 ** 40):
            self.assertEqual(cc.chrome_time(value), "")

    def test_wal_rows_are_read_without_modifying_original_sidecars(self):
        history = next(path for path, _ in self.inputs if path.name == "History")
        writer = sqlite3.connect(history)
        self.addCleanup(writer.close)
        writer.execute("PRAGMA journal_mode=WAL")
        writer.execute("INSERT INTO urls VALUES(4,?,?)", (POST_URL, "Only in WAL"))
        writer.execute("INSERT INTO visits VALUES(4,4,?,0,1)", (BASE_TIME + 123,))
        writer.commit()
        sidecars = [(Path(str(history) + suffix), (str(history) + suffix)) for suffix in ("-wal", "-shm")]
        inputs = self.inputs + [(path, path.relative_to(self.source).as_posix()) for path, _ in sidecars]
        before = {str(path): (cv.file_hash(path), path.stat().st_mtime_ns) for path, _ in inputs}
        result = self.context(inputs)
        resource = next(iter(result["resources"].values()))
        self.assertEqual(len([a for a in resource["activities"] if a["kind"] == "History visit"]), 3)
        self.assertEqual(before, {str(path): (cv.file_hash(path), path.stat().st_mtime_ns) for path, _ in inputs})
        self.assertTrue(any(name.endswith("-wal") for name in result["source_sha256"]))

    def test_context_source_mutation_aborts(self):
        original = cc.entry_metadata
        mutated = False

        def change(path):
            nonlocal mutated
            result = original(path)
            if not mutated:
                with Path(path).open("ab") as handle:
                    handle.write(b"changed")
                mutated = True
            return result

        with patch.object(cc, "entry_metadata", side_effect=change), self.assertRaisesRegex(ValueError, "source changed"):
            self.context()

    def test_source_changed_between_recovery_and_context_aborts(self):
        path = self.source / next(iter(self.manifest["sources"].values()))["path"]
        with path.open("ab") as handle:
            handle.write(b"changed")
        with self.assertRaisesRegex(ValueError, "before context"):
            self.context()

    def test_one_artifact_emits_overview_and_deduplicated_timeline_in_one_pass(self):
        context = FileContext(self.source, self.inputs, self.root / "report")
        before = {str(path): (cv.file_hash(path), path.stat().st_mtime_ns) for path, _ in self.inputs}
        with patch.object(artifact, "logfunc"), patch.object(artifact, "check_in_embedded_media", return_value="media-ref"), \
             patch.object(artifact, "recover_files", wraps=cv.recover_files) as recovery, \
             patch.object(cc, "open_sqlite_db_readonly", side_effect=lambda path: sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)):
            headers, rows, _ = artifact.get_chromeCacheVideos.__wrapped__(context)
        self.assertEqual(recovery.call_count, 1)
        self.assertEqual(list(artifact.__artifacts_v2__), ["get_chromeCacheVideos"])
        self.assertEqual(len(rows), 1)
        values = dict(zip([h[0] if isinstance(h, tuple) else h for h in headers], rows[0]))
        self.assertEqual(values["Post Titles"], "Synthetic preview")
        self.assertEqual(values["Post URLs"], POST_URL)
        self.assertEqual(values["Media Role"], "Scrubber preview")
        self.assertEqual(values["Promoted (as stored)"], "Yes")
        self.assertIn(PAGE_URL, values["Related Browser URLs"])
        with sqlite3.connect(context.report / "_Timeline/tl.db") as db:
            events = db.execute("SELECT activity,datalist FROM data").fetchall()
        self.assertEqual(len(events), 17)
        self.assertEqual({activity for activity, _ in events}, {"Chrome Cache - Videos"})
        self.assertEqual(len(json.loads((context.report / "chromeCacheVideos_events.json").read_text())), 17)
        self.assertEqual(before, {str(path): (cv.file_hash(path), path.stat().st_mtime_ns) for path, _ in self.inputs})

    def test_real_report_layout_places_timeline_at_run_root(self):
        context = FileContext(self.source, self.inputs, self.root / "run/_HTML/Chromium")
        with patch.object(artifact, "logfunc"), patch.object(artifact, "check_in_embedded_media", return_value="media-ref"):
            artifact.get_chromeCacheVideos.__wrapped__(context)
        self.assertTrue((self.root / "run/_Timeline/tl.db").is_file())
        self.assertFalse((context.report / "_Timeline").exists())

    def test_public_context_exact_dates_and_no_invented_playback(self):
        source = self.root / "public"
        with zipfile.ZipFile(PUBLIC_CASE_ZIP) as archive:
            archive.extractall(source)
        inputs = [(path, path.relative_to(source).as_posix()) for path in sorted(source.rglob("*")) if path.is_file()]
        _, manifest = cv.recover_files([(p, r) for p, r in inputs if cc.cache_input(r)], self.root / "public_output")
        result = cc.build_context(inputs, manifest)
        events = cc.resource_events(result)
        self.assertEqual(len(manifest["clips"]), 12)
        self.assertEqual(len(result["resources"]), 3)
        self.assertEqual(Counter(event["kind"] for event in events),
                         {"HTTP request time": 3, "HTTP response time": 3, "Cache last used": 3,
                          "History visit": 4, "Session navigation": 3})
        self.assertEqual(result["diagnostics"]["media_history_playback_records_read"], 0)
        self.assertEqual(result["diagnostics"]["media_history_playbackSession_records_read"], 0)
        resource = next(r for r in result["resources"].values() if "4ocgl9m4jbt61" in r["urls"][0])
        self.assertEqual(resource["metadata"][0]["response_time"].isoformat(), "2021-04-17T17:50:30.502880+00:00")
        self.assertTrue(all(post["role"] == "Scrubber preview" for r in result["resources"].values() for post in r["posts"]))
        self.assertEqual({a["relation"] for r in result["resources"].values() for a in r["activities"]}, {"Post ID in cached request URL"})
        # Siblings can be available only under another spelling of the same user.
        split_views = [(p, r.replace("/data/data/", "/data/user/0/")
                        if p.name.endswith("_0") or p.name == "the-real-index" else r) for p, r in inputs]
        split = cc.build_context(split_views, manifest)
        self.assertEqual(len(cc.resource_events(split)), 16)
        self.assertTrue(all(r["metadata"][0]["response_time"] and r["metadata"][0]["last_used"] for r in split["resources"].values()))
        # Index-only metadata is still useful when an HTTP sibling was not acquired.
        missing = {"06b0441e4b13e306_0", "5c35d641eaad57ef_0", "f1bbe0daa4aa7ce5_0"}
        result = cc.build_context([(p, r) for p, r in inputs if p.name not in missing], manifest)
        events = cc.resource_events(result)
        self.assertEqual(Counter(event["kind"] for event in events),
                         {"Cache last used": 3, "History visit": 4, "Session navigation": 3})
        self.assertTrue(all("HTTP metadata unavailable" in event["relation"] for event in events if event["kind"] == "Cache last used"))


if __name__ == "__main__":
    unittest.main()
