"""Chrome Cache - Videos: path patterns, cached context joins and the artifact's rows.

The recovery engine is chromiumcacheprobe, vendored in scripts/vendor; its own tests
live in that repository. These tests cover what ALEAPP adds: which files the artifact
reads, how the HTTP and index times, Reddit posts and browser records are joined to
each recovered video, and what the artifact writes.
"""
# pylint: disable=protected-access  # the tests call the artifact's helpers directly

from collections import Counter
from contextlib import closing
import fnmatch
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

from admin.test.scripts.test_snss_parser import _file, _navigation
from scripts.artifacts import chromeCacheVideos as artifact
from scripts.vendor import chromiumcacheprobe as ccp

REPO_ROOT = Path(__file__).resolve().parents[3]
CASES = REPO_ROOT / "admin/test/cases/data/chromeCacheVideos"
CASE_ZIP = CASES / "testdata.chromeCacheVideos.get_chromeCacheVideos.case1.zip"
PUBLIC_CASE_ZIP = CASES / "testdata.chromeCacheVideos.get_chromeCacheVideos.case2.zip"

BASE_TIME = 13344473600000000
MEDIA_URL = "https://v.redd.it/synthetic/DASH_96.mp4"
POST_URL = "https://www.reddit.com/r/example/comments/test123/media/"
PAGE_URL = "https://www.reddit.com/r/example/comments/page123/context/"
PREFIX = "Dump/data/data/com.android.chrome/"
SOURCE_POST_ID = "Page open when the Reddit listing was fetched (source_post_id)"


def fragment_bodies():
    """The four synthetic MP4 fragments, without their cache entry framing."""
    parts = []
    with zipfile.ZipFile(CASE_ZIP) as archive:
        for name in sorted(n for n in archive.namelist() if n.endswith("_0")):
            body = archive.read(name)
            key_length = struct.unpack_from("<I", body, 12)[0]
            metadata_length = struct.unpack_from("<I", body, len(body) - 8)[0]
            parts.append(body[24 + key_length: len(body) - 24 - 32 - metadata_length - 24])
    return parts


def pickle_payload(body):
    return struct.pack("<I", len(body)) + body


def response_info(request=BASE_TIME, response=BASE_TIME + 1000):
    headers = (b"HTTP/1.1 206 Partial Content\x00Content-Type: video/mp4\x00"
               b"Date: Wed, 01 Jan 2020 00:00:00 GMT\x00Last-Modified: Tue, 01 Jan 2019 00:00:00 GMT\x00"
               b"Content-Range: bytes 0-999/1000\x00")
    body = struct.pack("<IqqI", 3, request, response, len(headers)) + headers
    return pickle_payload(body + b"\0" * (-len(body) % 4))


def cache_entry(body, key, metadata=None, encoding=""):
    raw = key.encode()
    if metadata is None:
        metadata = response_info()
        if encoding:
            headers = (b"HTTP/1.1 200 OK\x00Content-Type: application/json\x00"
                       b"Content-Encoding: " + encoding.encode() + b"\x00")
            info = struct.pack("<IqqI", 3, BASE_TIME, BASE_TIME + 1000, len(headers)) + headers
            metadata = pickle_payload(info + b"\0" * (-len(info) % 4))
    return (struct.pack("<QIIII", ccp.INITIAL_MAGIC, 9, len(raw), 0, 0) + raw + body
            + struct.pack("<QIIII", ccp.FINAL_MAGIC, 0, 0, 0, 0) + metadata
            + hashlib.sha256(raw).digest()
            + struct.pack("<QIIII", ccp.FINAL_MAGIC, 2, 0, len(metadata), 0))


def index_file(hashes):
    body = struct.pack("<QIQQI", ccp.INDEX_MAGIC, 9, len(hashes), 10000, 0)
    body += b"".join(struct.pack("<QqQ", int(value, 16), BASE_TIME + 2000 + number, 256 << 8)
                     for number, value in enumerate(hashes))
    body += struct.pack("<q", BASE_TIME + 9999)
    return struct.pack("<II", len(body), 0) + body


def feed_document():
    post = {"id": "test123", "title": "Synthetic preview", "permalink": "/r/example/comments/test123/media/",
            "promoted": True, "secure_media": {"reddit_video": {"scrubber_media_url": MEDIA_URL}}}
    return json.dumps({"data": [post]}).encode()


FEED_URL = "https://www.reddit.com/r/example/top.json?source_post_id=t3_page123"


def stage_context(root):
    """Synthetic cache, Reddit listing, History, Media History and tab session."""
    app = root / PREFIX
    cache = app / "cache/Cache_Data"
    cache.mkdir(parents=True)
    for number, part in enumerate(fragment_bodies()):
        (cache / f"{number:016x}_0").write_bytes(cache_entry(part, MEDIA_URL))
    index = cache / "index-dir/the-real-index"
    index.parent.mkdir()
    index.write_bytes(index_file([f"{number:016x}" for number in range(4)]))
    (cache / "feed_0").write_bytes(cache_entry(gzip.compress(feed_document(), mtime=0), FEED_URL))
    profile = app / "app_chrome/Default"
    profile.mkdir(parents=True)
    with closing(sqlite3.connect(profile / "History")) as db:
        db.executescript("CREATE TABLE urls(id INTEGER PRIMARY KEY,url TEXT,title TEXT); "
                         "CREATE TABLE visits(id INTEGER PRIMARY KEY,url INTEGER,visit_time INTEGER,"
                         "from_visit INTEGER,transition INTEGER);")
        for number, url in enumerate((PAGE_URL, POST_URL, "https://unrelated.invalid/"), 1):
            db.execute("INSERT INTO urls VALUES(?,?,?)", (number, url, "Synthetic page"))
            db.execute("INSERT INTO visits VALUES(?,?,?,?,?)", (number, number, BASE_TIME - number, 0, 1))
        db.commit()
    with closing(sqlite3.connect(profile / "Media History")) as db:
        db.executescript("CREATE TABLE playback(id INTEGER PRIMARY KEY,url TEXT,last_updated_time_s INTEGER,"
                         "watch_time_s INTEGER,has_video INTEGER,has_audio INTEGER); "
                         "CREATE TABLE playbackSession(id INTEGER PRIMARY KEY,url TEXT,last_updated_time_s INTEGER,"
                         "title TEXT,position_ms INTEGER,duration_ms INTEGER);")
        db.execute("INSERT INTO playback VALUES(1,?,?,12,1,0)", (MEDIA_URL, BASE_TIME // 1000000))
        db.execute("INSERT INTO playbackSession VALUES(1,?,?,?,100,200)",
                   (POST_URL, BASE_TIME // 1000000, "Synthetic session"))
        db.commit()
    sessions = profile / "Sessions"
    sessions.mkdir()
    (sessions / "Tabs_100").write_bytes(_file((1, _navigation(url=PAGE_URL, timestamp=BASE_TIME - 100))))
    return [(path, path.relative_to(root).as_posix()) for path in sorted(root.rglob("*")) if path.is_file()]


def read_only(path):
    return sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)


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


class PathPatternTests(unittest.TestCase):
    def test_patterns_cover_users_and_layouts_and_do_not_cross_apps(self):
        patterns = artifact.__artifacts_v2__["get_chromeCacheVideos"]["paths"]
        for source in ("data/data", "data/user/0", "data/user/10", "data_mirror/data_ce/null/0"):
            for layout in ("Cache", "Cache_Data", "Cache/Cache_Data"):
                path = f"root/{source}/com.android.chrome/cache/{layout}/0000_0"
                self.assertEqual(sum(fnmatch.fnmatchcase(path, p) for p in patterns), 1)
                self.assertEqual(sum(fnmatch.fnmatchcase(path.lower(), p.lower()) for p in patterns), 1)
        self.assertFalse(any(fnmatch.fnmatchcase("root/data/data/com.other/cache/Cache_Data/a", p)
                             for p in patterns))


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "input"
        self.inputs = stage_context(self.source)
        self.output, self.manifest = ccp.recover_files(
            [(path, relative) for path, relative in self.inputs if artifact._cache_input(relative)],
            self.root / "output")
        self.assertEqual(len(self.manifest["clips"]), 1)

    def context(self, inputs=None, manifest=None):
        with patch.object(artifact, "open_sqlite_db_readonly", side_effect=read_only):
            return artifact._build_context(self.inputs if inputs is None else inputs,
                                           self.manifest if manifest is None else manifest)

    def resource(self, inputs=None):
        resources, _ = self.context(inputs)
        return next(iter(resources.values()))

    def test_times_post_and_browser_links(self):
        resources, diagnostics = self.context()
        resource = next(iter(resources.values()))
        self.assertEqual(len(resource["metadata"]), 4)
        self.assertEqual(resource["metadata"][0]["request_time"], ccp.chrome_time(BASE_TIME))
        self.assertEqual(resource["metadata"][0]["last_used"], ccp.chrome_time(BASE_TIME + 2000))
        self.assertIsInstance(resource["metadata"][0]["headers"]["last-modified"][0], str)
        self.assertEqual(len(resource["posts"]), 1)
        self.assertTrue(resource["posts"][0]["promoted"])
        self.assertEqual(resource["posts"][0]["role"], "Scrubber preview")
        relations = Counter((a["kind"], a["relation"]) for a in resource["activities"])
        self.assertEqual(relations, {
            ("History visit", SOURCE_POST_ID): 1,
            ("History visit", "Exact permalink of the video's post"): 1,
            ("Session navigation", SOURCE_POST_ID): 1,
            ("Media History playback", "Exact video URL"): 1,
            ("Media History session", "Exact permalink of the video's post"): 1})
        self.assertEqual(diagnostics["history_records_read"], 3)

    def test_brotli_listing_is_read(self):
        try:
            import brotli  # pylint: disable=import-outside-toplevel
        except ImportError:
            self.skipTest("brotli package not installed")
        feed = next(path for path, _ in self.inputs if path.name == "feed_0")
        feed.write_bytes(cache_entry(brotli.compress(feed_document()), FEED_URL, encoding="br"))
        self.assertEqual(len(self.resource()["posts"]), 1)

    def test_undecodable_listing_is_counted_not_dropped_silently(self):
        feed = next(path for path, _ in self.inputs if path.name == "feed_0")
        feed.write_bytes(cache_entry(b"\xff\xfe not brotli", FEED_URL, encoding="br"))
        resources, diagnostics = self.context()
        self.assertFalse(next(iter(resources.values()))["posts"])
        self.assertEqual(diagnostics["cache_body_not_decoded"], 1)

    def test_time_proximity_without_url_relationship_does_not_join(self):
        history = next(path for path, _ in self.inputs if path.name == "History")
        with closing(sqlite3.connect(history)) as db:
            db.execute("UPDATE urls SET url='https://www.reddit.com/r/example/comments/other1/unrelated/'")
            db.commit()
        self.assertFalse(any(a["kind"] == "History visit" for a in self.resource()["activities"]))

    def test_multiple_profiles_withhold_browser_joins(self):
        history = next(path for path, _ in self.inputs if path.name == "History")
        other = history.parent.parent / "Profile 1/History"
        other.parent.mkdir()
        shutil.copyfile(history, other)
        resource = self.resource(self.inputs + [(other, other.relative_to(self.source).as_posix())])
        self.assertEqual(resource["profile_candidates"], ["Default", "Profile 1"])
        self.assertFalse(resource["activities"])
        self.assertEqual(len(resource["posts"]), 1)

    def test_oversize_profile_does_not_silently_remove_profile_ambiguity(self):
        history = next(path for path, _ in self.inputs if path.name == "History")
        other = history.parent.parent / "Profile 1/History"
        other.parent.mkdir()
        other.write_bytes(b"0" * 200000)
        with patch.object(artifact, "MAX_CONTEXT_INPUT", 100000):
            resources, diagnostics = self.context(self.inputs + [(other, other.relative_to(self.source).as_posix())])
        resource = next(iter(resources.values()))
        self.assertEqual(resource["profile_candidates"], ["Default", "Profile 1"])
        self.assertFalse(resource["activities"])
        self.assertEqual(diagnostics["oversized_context_inputs_skipped"], 1)

    def test_other_user_storage_and_evidence_root_do_not_join(self):
        ancillary = [(p, r) for p, r in self.inputs if "/app_chrome/" in r or p.name == "feed_0"]
        base = [(p, r) for p, r in self.inputs if (p, r) not in ancillary]
        for replacement in ("OtherDump/data/data", "Dump/data/user/10", "Dump/data/user_de/0"):
            with self.subTest(replacement=replacement):
                resource = self.resource(base + [(p, r.replace("Dump/data/data", replacement)) for p, r in ancillary])
                self.assertFalse(resource["activities"])
                self.assertFalse(resource["posts"])

    def test_unknown_index_does_not_discard_valid_http_dates(self):
        index = next(path for path, _ in self.inputs if path.name == "the-real-index")
        body = bytearray(index.read_bytes())
        struct.pack_into("<I", body, 16, 999)
        index.write_bytes(body)
        resource = self.resource()
        self.assertEqual(len(resource["metadata"]), 4)
        self.assertTrue(resource["metadata"][0]["response_time"])
        self.assertFalse(resource["metadata"][0]["last_used"])

    def test_wrong_sparse_sibling_key_is_rejected(self):
        cache = next(path.parent for path, _ in self.inputs if path.name == "0000000000000000_0")
        path = cache / "0000000000000000_s"
        key = b"https://v.redd.it/different/DASH_96.mp4"
        path.write_bytes(struct.pack("<QIIII", ccp.INITIAL_MAGIC, 9, len(key), 0, 0) + key)
        manifest = {"sources": {"s": {"path": path.relative_to(self.source).as_posix(), "url": key.decode()}},
                    "clips": [{"source": "s", "sha256": "synthetic"}]}
        with patch.object(artifact, "open_sqlite_db_readonly", return_value=None):
            resources, diagnostics = artifact._build_context(
                self.inputs + [(path, path.relative_to(self.source).as_posix())], manifest)
        self.assertEqual(diagnostics["metadata_cache_key_mismatch"], 1)
        self.assertFalse(next(iter(resources.values()))["metadata"])

    def test_invalid_key_digest_and_oversized_body_are_rejected(self):
        path = self.root / "bad_0"
        body = bytearray(cache_entry(b"", MEDIA_URL))
        body[-25] ^= 1
        path.write_bytes(body)
        with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
            ccp.entry_metadata(path)
        path.write_bytes(cache_entry(gzip.compress(b"[" + b" " * 2048 + b"]"),
                                     "https://www.reddit.com/top.json", encoding="gzip"))
        with self.assertRaises(ccp.BodyError):
            ccp.entry_body(path, limit=1024)

    def test_missing_metadata_keeps_the_recovered_resource(self):
        inputs = [(p, r) for p, r in self.inputs if p.name.endswith("_0") and p.name != "feed_0"]
        resource = self.resource(inputs)
        self.assertFalse(resource["posts"])
        self.assertFalse(resource["activities"])
        self.assertTrue(all(record["response_time"] for record in resource["metadata"]))
        # Unreadable stream 0 metadata is never replaced by a file time.
        for path, _ in self.inputs:
            if path.name.endswith("_0"):
                payload = bytearray(path.read_bytes())
                length = struct.unpack_from("<I", payload, len(payload) - 8)[0]
                struct.pack_into("<I", payload, len(payload) - 24 - 32 - length + 4, 0)
                path.write_bytes(payload)
        for source in self.manifest["sources"].values():
            source["sha256"] = ccp.file_hash(self.source / source["path"])
        resource = self.resource(inputs)
        self.assertFalse(any(record["response_time"] or record["request_time"] for record in resource["metadata"]))

    def test_other_cache_directory_and_partition_do_not_join_posts(self):
        changed = [(p, r.replace("cache/Cache_Data/feed_0", "cache/Other/feed_0") if p.name == "feed_0" else r)
                   for p, r in self.inputs]
        self.assertFalse(self.resource(changed)["posts"])
        path = next(path for path, _ in self.inputs if path.name == "feed_0")
        body = path.read_bytes()
        key, spans, _ = ccp.cache_spans(body)
        path.write_bytes(cache_entry(body[spans[0].start:spans[0].end], "1/0/_dk_https://other.invalid " + key))
        self.assertFalse(self.resource()["posts"])

    def test_different_rendition_or_query_token_does_not_match(self):
        path = next(path for path, _ in self.inputs if path.name == "feed_0")
        key, spans, _ = ccp.cache_spans(path.read_bytes())
        original = gzip.decompress(path.read_bytes()[spans[0].start:spans[0].end])
        for replacement in (MEDIA_URL.replace("96", "720"), MEDIA_URL + "?token=other", MEDIA_URL + "/"):
            with self.subTest(replacement=replacement):
                path.write_bytes(cache_entry(original.replace(MEDIA_URL.encode(), replacement.encode()), key))
                self.assertFalse(self.resource()["posts"])

    def test_wal_rows_are_read_without_modifying_original_sidecars(self):
        history = next(path for path, _ in self.inputs if path.name == "History")
        writer = sqlite3.connect(history)
        self.addCleanup(writer.close)
        writer.execute("PRAGMA journal_mode=WAL")
        writer.execute("INSERT INTO urls VALUES(4,?,?)", (POST_URL, "Only in WAL"))
        writer.execute("INSERT INTO visits VALUES(4,4,?,0,1)", (BASE_TIME + 123,))
        writer.commit()
        sidecars = [Path(str(history) + suffix) for suffix in ("-wal", "-shm")]
        inputs = self.inputs + [(path, path.relative_to(self.source).as_posix()) for path in sidecars]
        before = {str(path): (ccp.file_hash(path), path.stat().st_mtime_ns) for path, _ in inputs}
        resource = self.resource(inputs)
        self.assertEqual(len([a for a in resource["activities"] if a["kind"] == "History visit"]), 3)
        self.assertEqual(before, {str(path): (ccp.file_hash(path), path.stat().st_mtime_ns) for path, _ in inputs})

    def test_context_source_mutation_aborts(self):
        original = ccp.entry_metadata
        mutated = False

        def change(path):
            nonlocal mutated
            result = original(path)
            if not mutated:
                with Path(path).open("ab") as handle:
                    handle.write(b"changed")
                mutated = True
            return result

        with patch.object(ccp, "entry_metadata", side_effect=change), \
                self.assertRaisesRegex(ValueError, "source changed"):
            self.context()

    def test_source_changed_between_recovery_and_context_aborts(self):
        path = self.source / next(iter(self.manifest["sources"].values()))["path"]
        with path.open("ab") as handle:
            handle.write(b"changed")
        with self.assertRaisesRegex(ValueError, "before context"):
            self.context()

    def test_artifact_rows_store_each_clip_once(self):
        report = self.root / "report"
        context = FileContext(self.source, self.inputs, report)
        before = {str(path): (ccp.file_hash(path), path.stat().st_mtime_ns) for path, _ in self.inputs}
        with patch.object(artifact, "logfunc"), \
                patch.object(artifact, "check_in_embedded_media", return_value="media-ref") as check_in, \
                patch.object(artifact, "open_sqlite_db_readonly", side_effect=read_only):
            headers, rows, _ = artifact.get_chromeCacheVideos.__wrapped__(context)
        self.assertEqual(len(rows), 1)
        self.assertEqual(check_in.call_count, 1)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        self.assertEqual(names[:4], ["Response Time", "Request Time", "Last Used", "Video"])
        values = dict(zip(names, rows[0]))
        self.assertEqual((values["Video Frames"], values["Width"], values["Height"], values["Audio"]),
                         (60, 96, 64, "No"))
        self.assertEqual(values["Post Titles"], "Synthetic preview")
        self.assertEqual(values["Post URLs"], POST_URL)
        self.assertEqual(values["Promoted (as stored)"], "Yes")
        self.assertIn(PAGE_URL, values["Linked Browser URLs"])
        self.assertIn(SOURCE_POST_ID, values["Browser Relationship"])
        self.assertEqual(len(json.loads(values["Source File"])), 4)
        # Only the provenance file is written beside the report; no clip copies or event files.
        self.assertEqual(sorted(p.name for p in report.rglob("*")), [artifact.PROVENANCE])
        provenance = json.loads((report / artifact.PROVENANCE).read_text())
        self.assertNotIn(str(self.root), json.dumps(provenance))
        self.assertEqual(before, {str(path): (ccp.file_hash(path), path.stat().st_mtime_ns) for path, _ in self.inputs})

    def test_public_dfrws_cache_context(self):
        source = self.root / "public"
        with zipfile.ZipFile(PUBLIC_CASE_ZIP) as archive:
            archive.extractall(source)
        inputs = [(path, path.relative_to(source).as_posix()) for path in sorted(source.rglob("*")) if path.is_file()]
        _, manifest = ccp.recover_files([(p, r) for p, r in inputs if artifact._cache_input(r)], self.root / "public_out")
        resources, diagnostics = artifact._build_context(inputs, manifest)
        self.assertEqual(len(manifest["clips"]), 12)
        self.assertEqual(len(resources), 3)
        self.assertEqual(diagnostics["media_history_playback_records_read"], 0)
        resource = next(r for r in resources.values() if "4ocgl9m4jbt61" in r["urls"][0])
        self.assertEqual(resource["metadata"][0]["response_time"].isoformat(), "2021-04-17T17:50:30.502880+00:00")
        self.assertTrue(all(post["role"] == "Scrubber preview" for r in resources.values() for post in r["posts"]))
        # Every browser link on this image is the page open when the listing was fetched.
        self.assertEqual({a["relation"] for r in resources.values() for a in r["activities"]}, {SOURCE_POST_ID})
        self.assertEqual(Counter(a["kind"] for r in resources.values() for a in r["activities"]),
                         {"History visit": 5, "Session navigation": 4})
        # Siblings can be present only under another spelling of the same user.
        split_views = [(p, r.replace("/data/data/", "/data/user/0/")
                        if p.name.endswith("_0") or p.name == "the-real-index" else r) for p, r in inputs]
        split, _ = artifact._build_context(split_views, manifest)
        self.assertTrue(all(r["metadata"][0]["response_time"] and r["metadata"][0]["last_used"]
                            for r in split.values()))
        # Index times still come through when the HTTP sibling was not acquired.
        missing = {"06b0441e4b13e306_0", "5c35d641eaad57ef_0", "f1bbe0daa4aa7ce5_0"}
        partial, _ = artifact._build_context([(p, r) for p, r in inputs if p.name not in missing], manifest)
        for resource in partial.values():
            self.assertTrue(all(record["last_used"] and not record["response_time"] for record in resource["metadata"]))
            self.assertTrue(all("HTTP metadata unavailable" in record["join_method"] for record in resource["metadata"]))


if __name__ == "__main__":
    unittest.main()
