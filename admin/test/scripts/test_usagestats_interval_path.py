"""Classify real XML/protobuf records from selected-store directory components."""
import collections
import datetime
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.artifacts import usagestats as mod
from scripts.artifacts.usagestats_pb import usagestatsservice_pb2 as v1
from scripts.artifacts.usagestats_pb import usagestatsservice_v2_pb2 as v2

CASES = {'daily': 'daily', 'weekly': 'weekly', 'monthly': 'monthly',
         'yearly': 'yearly', 'notdaily': '', 'case/WEEKLY': '', 'other/daily': 'daily',
         'daily/weekly': '', 'daily/daily': '', 'unknown': ''}


def fixture_bytes(kind):
    if kind == 'XML':
        return (b'<usagestats><packages><package package="org.example.app" lastTimeActive="1000" timeActive="2000"/></packages>'
                b'<configurations><config lastTimeActive="2000" timeActive="3000"/></configurations>'
                b'<event-log><event package="org.example.app" class="Main" time="3000" type="1" flags="7"/></event-log></usagestats>'), None
    stats = getattr(v1, 'IntervalStatsProto')() if kind == 'V1' else getattr(v2, 'IntervalStatsObfuscatedProto')()
    package = stats.packages.add()
    package.last_time_active_ms = 1000
    package.total_time_active_ms = 2000
    config = stats.configurations.add()
    config.last_time_active_ms = 2000
    config.total_time_active_ms = 3000
    event = stats.event_log.add()
    event.time_ms, event.type, event.flags = 3000, 1, 7
    if kind == 'V1':
        stats.stringpool.strings.extend(['org.example.app', 'Main'])
        package.package_index = 1
        event.package_index, event.class_index = 1, 2
        return stats.SerializeToString(), None
    package.package_token = 10
    event.package_token, event.class_token = 10, 2
    mapping = getattr(v2, 'ObfuscatedPackagesProto')()
    entry = mapping.packages_map.add()
    entry.package_token = 10
    entry.strings.extend(['org.example.app', 'Main'])
    return stats.SerializeToString(), mapping.SerializeToString()


def make_store(root, kind, cases=None):
    cases = CASES if cases is None else cases
    data, mapping = fixture_bytes(kind)
    for relative in cases:
        path = Path(root) / relative / '1700000000000'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(0o444)
    if mapping is not None:
        path = Path(root) / 'mappings'
        path.write_bytes(mapping)
        path.chmod(0o444)


class IntervalPathTest(unittest.TestCase):
    def test_actual_formats_native_records_and_host_invariance(self):
        for kind in ['XML', 'V1', 'V2']:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                previous = None
                for host in ['neutral', 'daily-report', 'weekly-monthly-yearly-report']:
                    root = Path(temporary) / host / 'data/system_ce/10/usagestats'
                    make_store(root, kind)
                    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
                    with patch.object(mod, 'logfunc'):
                        rows = mod.process_usagestats(str(root), '10', 2 if kind == 'V2' else 1)
                    self.assertEqual(len(rows), 3 * len(CASES))
                    self.assertTrue(all(len(row) == 26 and row[0] == '10' for row in rows))
                    self.assertEqual(collections.Counter(row[25] for row in rows), collections.Counter(label for label in CASES.values() for _ in range(3)))
                    self.assertEqual(collections.Counter(row[2] for row in rows), {'packages': 10, 'configurations': 10, 'event-log': 10})
                    for row in rows:
                        offset = {'packages': 1, 'configurations': 2, 'event-log': 3}[row[2]]
                        self.assertEqual(row[1], datetime.datetime.fromtimestamp(1700000000 + offset, tz=datetime.timezone.utc))
                        if row[2] == 'event-log':
                            self.assertEqual((row[11], row[12], row[13], row[14]), ('org.example.app', 'ACTIVITY_RESUMED', 'Main', '7'))
                    if previous is not None:
                        self.assertEqual(rows, previous)
                        self.assertEqual([[type(v) for v in row] for row in rows], [[type(v) for v in row] for row in previous])
                    previous = rows
                    self.assertEqual(before, {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()})

    def test_boundaries_and_directory_only(self):
        root = os.path.join(os.sep, 'host-daily', 'store')
        classify = mod._usage_interval  # pylint: disable=protected-access
        self.assertEqual(classify(os.path.join(root, 'weekly', '123'), root), 'weekly')
        for relative in ['daily-file', 'notdaily/123', 'WEEKLY/123', 'daily/weekly/123', 'daily/daily/123', '../daily/123', '123']:
            self.assertEqual(classify(os.path.join(root, relative), root), '')
        with patch.object(mod.os.path, 'relpath', side_effect=ValueError('different drives')):
            self.assertEqual(classify('file', 'store'), '')
        if os.sep == '/':
            self.assertEqual(classify(root + '/daily\\weekly/123', root), '')

    def test_unknown_after_known_and_duplicate_occurrences(self):
        with tempfile.TemporaryDirectory(prefix='daily-host-') as temporary:
            root = Path(temporary) / 'system/usagestats/0'
            make_store(root, 'XML', {'weekly': 'weekly', 'unknown': ''})
            with patch.object(mod, 'logfunc'):
                rows = mod.process_usagestats(str(root), '0', 1)
            self.assertEqual(len(rows), 6)
            self.assertEqual(collections.Counter(row[-1] for row in rows), {'weekly': 3, '': 3})
            self.assertEqual(len([row for row in rows if row[2] == 'event-log']), 2)


if __name__ == '__main__':
    unittest.main()
