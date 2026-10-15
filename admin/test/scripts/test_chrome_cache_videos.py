"""Known-content video fixtures; runtime recovery requires no external programs."""

import fnmatch
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
from scripts import chrome_cache_video as cv  # pylint: disable=wrong-import-position
from scripts.artifacts import (
    chromeCacheVideos as artifact,
)  # pylint: disable=wrong-import-position

CASE_ZIP = (
    REPO_ROOT / "admin/test/cases/data/chromeCacheVideos/"
    "testdata.chromeCacheVideos.get_chromeCacheVideos.case1.zip"
)
PUBLIC_CASE_ZIP = CASE_ZIP.with_name(
    "testdata.chromeCacheVideos.get_chromeCacheVideos.case2.zip"
)


def fixture():
    with zipfile.ZipFile(CASE_ZIP) as archive:
        dense = [
            archive.read(name)
            for name in sorted(archive.namelist())
            if name.endswith("_0")
        ]
        init = (CASE_ZIP.parent / "synthetic_initialization.mp4").read_bytes()
    parts = []
    for body in dense:
        key_length = struct.unpack_from("<I", body, 12)[0]
        metadata_length = struct.unpack_from("<I", body, len(body) - 8)[0]
        parts.append(body[24 + key_length : len(body) - 24 - 32 - metadata_length - 24])
    return parts, init


def wrap_cache(body, url, partition="https://page.invalid"):
    key = ("1/0/_dk_" + partition + " " + url).encode()
    metadata = b"HTTP/1.1 200 OK\x00Content-Type: video/mp4\x00"
    return (
        struct.pack("<QIIII", cv.INITIAL_MAGIC, 9, len(key), 0, 0)
        + key
        + body
        + struct.pack("<QIIII", cv.FINAL_MAGIC, 0, 0, 0, 0)
        + metadata
        + hashlib.sha256(key).digest()
        + struct.pack("<QIIII", cv.FINAL_MAGIC, 2, 0, len(metadata), 0)
    )


def sparse_cache(body, url):
    key = url.encode()
    return (
        struct.pack("<QIIII", cv.INITIAL_MAGIC, 9, len(key), 0, 0)
        + key
        + struct.pack("<QQQII", cv.SPARSE_MAGIC, 4096, len(body), 0, 0)
        + body
    )


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.parts, self.init = fixture()

    def stage(self, indices=None, container="dense", init=False, scope="data/data"):
        directory = self.root / scope / "com.android.chrome/cache/Cache_Data"
        directory.mkdir(parents=True, exist_ok=True)
        pairs = []
        for index in range(4) if indices is None else indices:
            body = self.parts[index]
            url = f"https://video.invalid/pattern_part{index}.mp4?token=synthetic&bytestart={index * 100}"
            if container == "dense":
                body = wrap_cache(body, url)
            elif container == "sparse":
                body = sparse_cache(body, url)
            name = f"{index:016x}_0" if container != "raw" else f"clip_part{index}.mp4"
            path = directory / name
            path.write_bytes(body)
            pairs.append((path, str(path.relative_to(self.root))))
        if init:
            path = directory / "initialization_0"
            path.write_bytes(
                wrap_cache(
                    self.init, "https://video.invalid/pattern.mp4?token=synthetic"
                )
            )
            pairs.append((path, str(path.relative_to(self.root))))
        return pairs

    def recover(self, pairs, **kwargs):
        before = {
            path: (cv.file_hash(path), path.stat().st_mtime_ns) for path, _ in pairs
        }
        output, report = cv.recover_files(pairs, self.root / "output", **kwargs)
        self.assertEqual(report["status"], "completed", report)
        self.assertEqual(
            before,
            {path: (cv.file_hash(path), path.stat().st_mtime_ns) for path, _ in pairs},
        )
        self.assertTrue((output / "provenance.json").is_file())
        for clip in report["clips"]:
            self.assertEqual(clip["decoder_check"], "not_performed")
            self.assertEqual(cv.file_hash(output / clip["file"]), clip["sha256"])
        self.assertNotIn(str(self.root), (output / "provenance.json").read_text())
        return output, report

    def test_dense_known_frame_count_and_timebase(self):
        _, report = self.recover(self.stage())
        self.assertEqual(len(report["clips"]), 1)
        clip = report["clips"][0]
        self.assertEqual(
            (clip["video_frames"], clip["video_seconds"], clip["timescale"]),
            (60, 2.021333333333333, 90000),
        )
        self.assertEqual((clip["width"], clip["height"]), (96, 64))
        self.assertFalse(clip["audio"])
        self.assertTrue(clip["sample_bytes_verified"])
        self.assertIn("other_tracks_omitted", clip["warnings"])

    def test_raw_exported_parts(self):
        _, report = self.recover(self.stage(container="raw"))
        self.assertEqual(report["clips"][0]["video_frames"], 60)

    def test_sparse_bounded_ranges(self):
        _, report = self.recover(self.stage(container="sparse"))
        self.assertEqual(report["clips"][0]["video_frames"], 60)
        self.assertEqual(report["statistics"]["span_simple_sparse_range"], 4)

    def test_original_initialization_supplies_audio_and_provenance(self):
        _, report = self.recover(self.stage(init=True))
        clip = report["clips"][0]
        self.assertTrue(clip["audio"])
        self.assertNotIn("video_header_reconstructed", clip["warnings"])
        self.assertEqual(len(clip["initialization_sources"]), 1)
        self.assertEqual(clip["samples"]["2"]["count"], 95)

    def test_gap_restarts_at_idr(self):
        _, report = self.recover(self.stage(indices=[0, 2, 3]))
        self.assertEqual([clip["video_frames"] for clip in report["clips"]], [15, 30])

    def test_missing_idr_drops_leading_samples(self):
        _, report = self.recover(self.stage(indices=[1, 2, 3]))
        self.assertEqual([clip["video_frames"] for clip in report["clips"]], [30])

    def test_same_url_in_two_android_users_stays_separate(self):
        pairs = self.stage() + self.stage(scope="data/user/10")
        _, report = self.recover(pairs)
        self.assertEqual(len(report["clips"]), 2)
        for clip in report["clips"]:
            paths = {
                report["sources"][sample["source"]]["path"]
                for track in clip["tracks"]
                for sample in track["source_samples"]
            }
            self.assertEqual(
                len({path.split("/com.android.chrome/")[0] for path in paths}), 1
            )

    def test_partition_keys_stay_separate(self):
        pairs = self.stage()
        for index, part in enumerate(self.parts):
            path = pairs[0][0].parent / f"partition_{index}_0"
            path.write_bytes(
                wrap_cache(
                    part,
                    f"https://video.invalid/pattern_part{index}.mp4?token=synthetic&bytestart={index * 100}",
                    partition="https://other.invalid",
                )
            )
            pairs.append((path, str(path.relative_to(self.root))))
        _, report = self.recover(pairs)
        self.assertEqual(len(report["clips"]), 2)

    def test_duplicate_fragments_and_selected_paths(self):
        pairs = self.stage()
        path = pairs[0][0].parent / "duplicate_0"
        path.write_bytes(pairs[0][0].read_bytes())
        pairs.append((path, str(path.relative_to(self.root))))
        _, report = self.recover(pairs + pairs)
        self.assertEqual(report["clips"][0]["video_frames"], 60)
        self.assertEqual(report["statistics"]["duplicate_fragments"], 1)
        self.assertEqual(report["statistics"]["files_seen"], 5)

    def test_no_inferred_timebase(self):
        pairs = self.stage(container="raw")
        for path, _ in pairs:
            path.write_bytes(path.read_bytes()[64:])  # two 32-byte sidx boxes
        _, report = self.recover(pairs)
        self.assertFalse(report["clips"])
        self.assertGreater(report["statistics"]["missing_video_timescale"], 0)

    def test_conflicting_sample_is_not_selected(self):
        pairs = self.stage()
        probe = self.root / "probe.mp4"
        probe.write_bytes(self.parts[0])
        fragments, _, _, _ = cv.scan_file(probe, "probe", cv.Counter(), None)
        _, parsed = cv.parse_fragment(fragments[0], {})
        sample = parsed[1][0]
        damaged = bytearray(self.parts[0])
        damaged[sample.offset + sample.size - 1] ^= 1
        path = pairs[0][0].parent / "conflict_0"
        path.write_bytes(
            wrap_cache(
                damaged,
                "https://video.invalid/pattern_part0.mp4?token=synthetic&bytestart=0",
            )
        )
        pairs.append((path, str(path.relative_to(self.root))))
        _, report = self.recover(pairs)
        self.assertEqual(sum(clip["video_frames"] for clip in report["clips"]), 30)
        self.assertGreater(report["statistics"]["conflicting_samples_skipped"], 0)

    def test_source_change_invalidates_outputs(self):
        pairs = self.stage()

        def mutate(message, **_kwargs):
            if message == "parsing_fragments":
                with pairs[0][0].open("ab") as stream:
                    stream.write(b"mutation")

        output, report = cv.recover_files(pairs, self.root / "output", progress=mutate)
        self.assertEqual(report["status"], "failed")
        self.assertFalse(report["clips"])
        self.assertFalse(list((output / "Videos").iterdir()))

    def test_complete_mp4_copied_byte_for_byte(self):
        output, first = self.recover(self.stage())
        media = (output / first["clips"][0]["file"]).read_bytes()
        path = self.root / "copy_input/complete_0"
        path.parent.mkdir()
        path.write_bytes(wrap_cache(media, "https://video.invalid/complete.mp4"))
        output, report = self.recover([(path, "copy_input/complete_0")])
        self.assertEqual(report["clips"][0]["kind"], "complete_mp4_carved")
        self.assertEqual((output / report["clips"][0]["file"]).read_bytes(), media)

    def test_malformed_and_truncated_inputs(self):
        path = self.root / "malformed_input/bad"
        path.parent.mkdir()
        for body in [b"", b"\x00\x00\x00\x08moof", self.parts[0][:-10], b"moof" * 1000]:
            path.write_bytes(body)
            _, report = self.recover([(path, "malformed")])
            self.assertFalse(report["clips"])

    def test_output_inside_input_rejected(self):
        pairs = self.stage()
        with self.assertRaises(ValueError):
            cv.recover_files(pairs, pairs[0][0].parent / "output")

    def test_conflicting_adjacent_timebases_are_rejected(self):
        pairs = self.stage(container="raw", indices=[0])
        path = pairs[0][0]
        second = cv.full(b"sidx", 0, 0, struct.pack(">IIIIHH", 1, 48000, 0, 0, 0, 0))
        path.write_bytes(path.read_bytes()[:32] + second + path.read_bytes()[64:])
        _, report = self.recover(pairs)
        self.assertFalse(report["clips"])
        self.assertEqual(report["statistics"]["conflicting_timescales"], 1)

    def test_encrypted_sample_metadata_is_rejected(self):
        path = self.root / "encrypted.mp4"
        moof = cv.atom(
            b"moof",
            cv.full(b"mfhd", 0, 0, struct.pack(">I", 1)),
            cv.atom(b"traf", cv.full(b"senc", 0, 0)),
        )
        path.write_bytes(moof + cv.atom(b"mdat", b"sample"))
        frag = cv.Fragment(
            path, "encrypted", "group", 0, len(moof), len(moof), 14, 8, {}, ""
        )
        with self.assertRaisesRegex(
            cv.FormatError, "encrypted_or_auxiliary_samples_unsupported"
        ):
            cv.parse_fragment(frag, {})

    def test_large_clips_are_not_registered(self):
        pairs = self.stage()
        with patch.object(cv, "MAX_CLIP_BYTES", 32):
            _, report = self.recover(pairs)
        self.assertFalse(report["clips"])
        self.assertGreater(report["statistics"]["clip_size_limit"], 0)

    def test_path_patterns_cover_users_and_do_not_cross_apps(self):
        patterns = artifact.__artifacts_v2__["get_chromeCacheVideos"]["paths"]
        for source in [
            "data/data",
            "data/user/0",
            "data/user/10",
            "data_mirror/data_ce/null/0",
        ]:
            for layout in ("Cache", "Cache_Data", "Cache/Cache_Data"):
                path = f"root/{source}/com.android.chrome/cache/{layout}/0000_0"
                self.assertEqual(
                    sum(fnmatch.fnmatchcase(path, pattern) for pattern in patterns), 1
                )
                self.assertEqual(
                    sum(fnmatch.fnmatchcase(path.lower(), pattern.lower()) for pattern in patterns), 1
                )
        self.assertFalse(
            any(
                fnmatch.fnmatchcase(
                    "root/data/data/com.other/cache/Cache_Data/a", pattern
                )
                for pattern in patterns
            )
        )

    def test_artifact_rows_and_storage_views(self):
        from scripts.context import Context  # pylint: disable=import-outside-toplevel

        pairs = self.stage()
        mirror = self.stage(scope="data/user/0")
        with patch.multiple(
            Context,
            _data_folder=str(self.root),
            _report_folder=str(self.root / "report"),
            _files_found=[str(path) for path, _ in pairs + mirror],
            _filename_lookup_map={},
        ), patch.object(
            Context, "get_relative_path",
            side_effect=lambda path: Path(path).relative_to(self.root).as_posix().replace("/", "\\"),
        ), patch.object(
            artifact, "check_in_embedded_media", return_value="media-ref"
        ), patch.object(artifact, "logfunc"):
            headers, rows, _ = artifact.get_chromeCacheVideos.__wrapped__(Context)
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(headers), len(rows[0]))
        values = dict(zip([h[0] if isinstance(h, tuple) else h for h in headers], rows[0]))
        self.assertEqual(tuple(values[name] for name in ("Video Frames", "Video Seconds", "Width", "Height", "Audio", "Video Timebase")),
                         (60, 2.021333333333333, 96, 64, "No", 90000))
        self.assertEqual(len(json.loads(values["Source File"])), 4)
        self.assertNotIn("\\", values["Source File"])

    def test_public_dfrws_cache_regression(self):
        source = self.root / "public"
        with zipfile.ZipFile(PUBLIC_CASE_ZIP) as archive:
            archive.extractall(source)
        pairs = [(path, path.relative_to(source).as_posix())
                 for path in sorted(source.rglob("*")) if path.is_file()]
        expected = json.loads((CASE_ZIP.parent / "dfrws2021_sources.json").read_text())
        self.assertEqual(
            {relative: cv.file_hash(path) for path, relative in pairs},
            expected["source_sha256"],
        )
        _, report = self.recover(pairs)
        self.assertEqual(len(report["clips"]), 12)
        self.assertEqual(report["statistics"]["fragments_found"], 35)
        self.assertEqual(report["statistics"]["resource_groups"], 3)
        self.assertEqual(sum(clip["video_frames"] for clip in report["clips"]), 170)
        self.assertEqual({(c["width"], c["height"]) for c in report["clips"]}, {(170, 96)})
        self.assertEqual({c["sha256"] for c in report["clips"]}, set(expected["output_sha256"]))

    @unittest.skipUnless(
        shutil.which("ffmpeg") and shutil.which("ffprobe"),
        "Optional independent decoder tools unavailable",
    )
    def test_output_decodes_and_has_sixty_frames(self):
        output, report = self.recover(self.stage(init=True))
        video = output / report["clips"][0]["file"]
        subprocess.run(
            [
                "ffmpeg",
                "-nostdin",
                "-v",
                "error",
                "-xerror",
                "-i",
                str(video),
                "-f",
                "null",
                "-",
            ],
            check=True,
            capture_output=True,
        )
        streams = json.loads(
            subprocess.check_output(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-count_frames",
                    "-show_streams",
                    "-of",
                    "json",
                    str(video),
                ]
            )
        )["streams"]
        self.assertEqual([stream["codec_name"] for stream in streams], ["h264", "aac"])
        self.assertEqual(streams[0]["nb_read_frames"], "60")


if __name__ == "__main__":
    unittest.main()
