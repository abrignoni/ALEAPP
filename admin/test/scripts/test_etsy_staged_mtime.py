"""Exercise cache summaries using controlled recorded times and real image bytes."""
import gzip
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.artifacts import etsy
from scripts.search_files import FileInfo, StagedTimes


class TestEtsyStagedMtime(unittest.TestCase):
    def run_summary(self, root, paths, infos=None):
        if infos is None:
            # as the folder seeker records a file: its own modification time, no StagedTimes
            infos = {str(p): FileInfo(str(p), 0, os.path.getmtime(p)) for p in paths}
        seeker = SimpleNamespace(file_infos=infos)
        context = SimpleNamespace(get_files_found=lambda: list(map(str, paths)),
                                  get_seeker=lambda: seeker,
                                  get_relative_path=lambda p: str(Path(p).relative_to(root)))
        return etsy.etsy_image_caches.__wrapped__(context)[1]

    def test_fractional_negative_extrema_and_gzip_sizes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            folder = root / 'data/user/0/com.etsy.android/cache/image_manager_disk_cache'
            folder.mkdir(parents=True)
            raw = b'\x89PNG\r\n\x1a\nsmall'
            bodies = [raw, gzip.compress(raw, mtime=0)]
            paths = []
            for i, (body, stamp) in enumerate(zip(bodies, [-2.75, -1.25])):
                p = folder / str(i)
                p.write_bytes(body)
                os.utime(p, (stamp, stamp))
                paths.append(p)
            row = self.run_summary(root, paths)[0]
            self.assertEqual(row[:2], (datetime.fromtimestamp(-1.25, timezone.utc),
                                      datetime.fromtimestamp(-2.75, timezone.utc)))
            self.assertEqual(row[2:4], ('', ''))
            self.assertEqual(row[5:8], (2, sum(map(len, bodies)), 'PNG 2'))

    def test_zero_and_journal_exclusion(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            folder = root / 'data/user/0/com.etsy.android/cache/image_manager_disk_cache'
            folder.mkdir(parents=True)
            p = folder / 'entry'
            p.write_bytes(b'unknown')
            os.utime(p, (0, 0))
            journal = folder / 'journal'
            journal.write_bytes(b'excluded')
            self.assertEqual(self.run_summary(root, [journal]), [])
            row = self.run_summary(root, [p, journal])[0]
            self.assertEqual(row[:4], ('', '', '', ''))
            self.assertEqual(row[5:8], (1, 7, 'Unrecognised 1'))

    def test_alias_rank_and_separate_user(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = []
            for prefix, body in [('data/user/0', b'unknown'),
                                 ('data/data', b'GIF89a'), ('data/user/10', b'GIF87a')]:
                p = root / prefix / 'com.etsy.android/cache/image_manager_disk_cache/same'
                p.parent.mkdir(parents=True)
                p.write_bytes(body)
                os.utime(p, (100, 100))
                paths.append(p)
            rows = self.run_summary(root, paths)
            self.assertEqual(len(rows), 2)
            self.assertEqual([r[7] for r in rows], ['GIF 1', 'GIF 1'])
            self.assertEqual(rows, self.run_summary(root, list(reversed(paths))))

    def test_no_recorded_time_and_size_failure(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = root / 'data/user/0/com.etsy.android/cache/image_manager_disk_cache/a'
            p.parent.mkdir(parents=True)
            p.write_bytes(b'GIF89a')
            os.utime(p, (100, 100))
            # the staged copy has a time and the input recorded none, so none is reported
            row = self.run_summary(root, [p], infos={})[0]
            self.assertEqual(row[:4], ('', '', '', ''))
            self.assertEqual(row[5:8], (1, 6, 'GIF 1'))
            with patch.object(etsy.os.path, 'getsize', side_effect=OSError('controlled')):
                row = self.run_summary(root, [p])[0]
            self.assertEqual(row[5:8], (1, 0, ''))

    def test_readings_with_no_zone_stay_apart_from_utc_times(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            folder = root / 'data/user/0/com.etsy.android/cache/image_manager_disk_cache'
            folder.mkdir(parents=True)
            infos, paths = {}, []
            recorded = (('a', None, '2024-06-01 12:00:00'), ('b', None, '2023-01-02 03:04:06'),
                        ('c', 1717261200, '2024-06-01 12:00:00'))
            for name, utc, reading in recorded:
                p = folder / name
                p.write_bytes(b'GIF89a')
                # a staged copy's time that must not reach the report
                os.utime(p, (5, 5))
                infos[str(p)] = FileInfo(name, 0, utc or 0,
                                         times=StagedTimes(modified=utc, modified_no_zone=reading))
                paths.append(p)
            row = self.run_summary(root, paths, infos=infos)[0]
            when = datetime.fromtimestamp(1717261200, timezone.utc)
            self.assertEqual(row[:4], (when, when, '2024-06-01 12:00:00', '2023-01-02 03:04:06'))


if __name__ == '__main__':
    unittest.main()
