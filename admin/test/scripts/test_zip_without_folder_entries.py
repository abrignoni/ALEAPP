"""Usage Stats and Recent Activity read a zip that stores no folder entries.

Both artifacts read a store folder (system_ce/<n>/usagestats, system_ce/<n>) rather than
single files, and found it only when the seeker returned the folder itself as a hit. A
folder input and a zip that stores folder entries do that. A zip that stores only file
entries does not, so both artifacts reported no data while the seeker had staged every
file. They now also take the folder as the parent of a file hit.

Each test stages the same small store from two zips, one with folder entries and one
without, through the zip seeker, and expects the same rows from both.
"""
import os
import pathlib
import sys
import tempfile
import unittest
import zipfile
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

# pylint: disable=wrong-import-position,no-member  # protobuf builds these names at run time
from scripts.search_files import FileSeekerZip
from scripts.artifacts import recentactivity, usagestats
from scripts.artifacts.usagestats_pb import usagestatsservice_v2_pb2

INTERVAL_START = 1700000000000


def _usagestats_members():
    mappings = usagestatsservice_v2_pb2.ObfuscatedPackagesProto()
    entry = mappings.packages_map.add()
    entry.package_token = 1
    entry.strings.append('com.example.app')
    stats = usagestatsservice_v2_pb2.IntervalStatsObfuscatedProto()
    package = stats.packages.add()
    package.package_token = 1
    package.last_time_active_ms = 1000
    package.total_time_active_ms = 5000
    return {
        'system_ce/0/usagestats/mappings': mappings.SerializeToString(),
        f'system_ce/0/usagestats/daily/{INTERVAL_START}': stats.SerializeToString(),
    }


def _recent_task_members():
    return {
        'system_ce/0/recent_tasks/7_task.xml':
            b'<?xml version="1.0" encoding="utf-8"?>\n'
            b'<task task_id="7" real_activity="com.example.app/.Main" '
            b'last_time_moved="1700000000000" />\n',
    }


def _write_zip(path, members, with_folders):
    with zipfile.ZipFile(path, 'w') as archive:
        if with_folders:
            folders = set()
            for name in members:
                parts = name.split('/')[:-1]
                for depth in range(1, len(parts) + 1):
                    folders.add('/'.join(parts[:depth]) + '/')
            for folder in sorted(folders):
                archive.writestr(folder, b'')
        for name, data in members.items():
            archive.writestr(name, data)


def _run(members, with_folders, pattern, function, case_folder=('report',)):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        zip_path = tmp_path / 'extraction.zip'
        _write_zip(zip_path, members, with_folders)
        data_folder = tmp_path.joinpath(*case_folder) / 'data'
        data_folder.mkdir(parents=True)
        seeker = FileSeekerZip(str(zip_path), str(data_folder))
        try:
            files = [str(path) for path in seeker.search(pattern)]
        finally:
            seeker.cleanup()
        context = SimpleNamespace(get_files_found=lambda: files,
                                  get_data_folder=lambda: str(data_folder))
        _headers, rows, source = function.__wrapped__(context)
        outside = [line for line in str(source).splitlines()
                   if line and not line.startswith(str(data_folder) + os.sep)]
    return rows, outside


def _rows(members, with_folders, pattern, function):
    return _run(members, with_folders, pattern, function)[0]


class ZipWithoutFolderEntries(unittest.TestCase):

    def test_usagestats_rows_match_with_and_without_folder_entries(self):
        members = _usagestats_members()
        pattern = '*/system_ce/*/usagestats*'
        with_folders = _rows(members, True, pattern, usagestats.get_usagestats)
        without_folders = _rows(members, False, pattern, usagestats.get_usagestats)
        self.assertEqual(len(with_folders), 1)
        self.assertEqual(without_folders, with_folders)

    def test_recent_activity_rows_match_with_and_without_folder_entries(self):
        members = _recent_task_members()
        pattern = '*/system_ce/*'
        with_folders = _rows(members, True, pattern, recentactivity.get_recentactivity)
        without_folders = _rows(members, False, pattern, recentactivity.get_recentactivity)
        self.assertEqual(len(with_folders), 1)
        self.assertEqual(without_folders, with_folders)

    def test_examiner_folders_named_like_a_store_are_not_read(self):
        # The case sits under folders named like the stores; only evidence is read.
        cases = (
            (_usagestats_members(), '*/system_ce/*/usagestats*', usagestats.get_usagestats,
             ('system_ce', '5', 'usagestats', 'report')),
            (_recent_task_members(), '*/system_ce/*', recentactivity.get_recentactivity,
             ('system_ce', '5', 'report')),
        )
        for members, pattern, function, case_folder in cases:
            with self.subTest(function=function.__name__):
                rows, outside = _run(members, False, pattern, function, case_folder)
                self.assertEqual(len(rows), 1)
                self.assertEqual(outside, [])
    def test_mirror_copy_listed_first_does_not_hide_the_store(self):
        members = _usagestats_members()
        mirrored = {name.replace('system_ce/', 'mirror/data/system_ce/', 1): data
                    for name, data in members.items()}
        ordered = dict(mirrored)
        ordered.update({name.replace('system_ce/', 'data/system_ce/', 1): data
                        for name, data in members.items()})
        rows = _rows(ordered, False, '*/system_ce/*/usagestats*', usagestats.get_usagestats)
        self.assertEqual(len(rows), 1)


if __name__ == '__main__':
    unittest.main()
