"""Actual SQLite fixtures check optional lookup without claiming vendor schema."""
import hashlib
import pathlib
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scripts.artifacts.WithingsHealthMate import healthmate_trackings

CATEGORY_IDS = [37, 272, 1, '1', 1.0, 0, None, 8, 9, 10, 11, 12, 37]
LOOKUP_ROWS = [(37, 'stored sleep'), (272, 'stored watch'), (1, 'integer one'),
               ('1', 'text one'), (1.0, 'float one'), (0, 0), (8, None), (9, ''),
               (10, 'same'), (10, 'same'), (11, 'first'), (11, 'second'),
               (12, None), (12, ''), (None, 'null does not match')]


def make_room(path):
    """Fourteen positional columns exercise the existing parser layout only."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE Track (' + ','.join(f'c{i}' for i in range(14)) + ')')
    rows = []
    for index, category in enumerate(CATEGORY_IDS):
        row = [None] * 14
        row[0:5] = [index, f'ws-{index}', 0, 1700000000123 + index * 1000,
                    1700000001123 + index * 1000]
        row[7], row[9], row[10], row[12], row[13] = (
            1700000002123 + index * 1000, 0, 'stored model', category, '{"raw":0}')
        rows.append(tuple(row))
    rows.append(rows[0])
    db.executemany('INSERT INTO Track VALUES (' + ','.join('?' for _ in range(14)) + ')', rows)
    db.commit()
    db.close()
    return path, rows


def make_lookup(path, rows=None, bad_schema=False, corrupt=False):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if corrupt:
        path.write_bytes(b'not a SQLite database')
        return path
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE activityCategory (' + ('other' if bad_schema else 'id,name') + ')')
    if not bad_schema:
        db.executemany('INSERT INTO activityCategory VALUES (?,?)', LOOKUP_ROWS if rows is None else rows)
    db.commit()
    db.close()
    return path


class Context:
    def __init__(self, root, files, relative_overrides=None):
        self.root = pathlib.Path(root)
        self.files = [str(p) for p in files]
        self.relative_overrides = relative_overrides or {}

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return self.relative_overrides.get(str(path), str(pathlib.Path(path).relative_to(self.root)))


class WithingsTrackingLookupTest(unittest.TestCase):
    def test_raw_typed_names_and_ids_keep_dates_rows_and_repeat(self):
        with tempfile.TemporaryDirectory() as folder:
            parent = pathlib.Path(folder) / 'data/user/0/com.withings.wiscale2/databases'
            room, originals = make_room(parent / 'room-healthmate')
            lookup = make_lookup(parent / 'Withings-WiScale')
            with patch('scripts.artifacts.WithingsHealthMate.logfunc') as log:
                headers, rows, source = healthmate_trackings.__wrapped__(Context(folder, [room, lookup]))
            self.assertEqual(len(headers), 12)
            self.assertEqual(headers[9:], ('Stored Activity Category Name', 'Tracking Data',
                                          'Category Lookup Status'))
            self.assertEqual(source, f'{room}\n{lookup}')
            self.assertEqual(len(rows), 14)
            self.assertEqual(rows[0], rows[-1])
            expected = [('stored sleep', 'matched-name'), ('stored watch', 'matched-name'),
                        ('integer one', 'matched-name'), ('text one', 'matched-name'),
                        ('float one', 'matched-name'), (0, 'matched-name'),
                        ('', 'missing-category-ID'), (None, 'matched-NULL-name'),
                        ('', 'matched-empty-name'), ('same', 'matched-name'),
                        ('', 'ambiguous-category'), ('', 'ambiguous-category'),
                        ('stored sleep', 'matched-name'), ('stored sleep', 'matched-name')]
            for report, original, (name, status) in zip(rows, originals, expected):
                self.assertEqual(report[9], name)
                self.assertIs(type(report[9]), type(name))
                self.assertEqual(report[11], status)
                self.assertEqual(report[3:9], tuple(original[i] for i in [0, 1, 2, 9, 10, 12]))
                self.assertIs(type(report[8]), type(original[12]))
                self.assertEqual(report[10], original[13])
                self.assertEqual([date.timestamp() for date in report[:3]],
                                 [int(original[i] / 1000) for i in [3, 4, 7]])
            self.assertEqual(log.call_count, 2)  # Each conflicting category logs once.

    def test_foreign_user_first_and_second_room_do_not_change_pair(self):
        with tempfile.TemporaryDirectory() as folder:
            base = pathlib.Path(folder)
            own = base / 'data/user/0/com.withings.wiscale2/databases'
            other = base / 'data/user/10/com.withings.wiscale2/databases'
            room, _ = make_room(own / 'room-healthmate')
            lookup = make_lookup(own / 'Withings-WiScale')
            foreign_lookup = make_lookup(other / 'Withings-WiScale', [(37, 'wrong user')])
            foreign_room, _ = make_room(other / 'room-healthmate')
            with patch('scripts.artifacts.WithingsHealthMate.logfunc'):
                _, rows, source = healthmate_trackings.__wrapped__(
                    Context(folder, [foreign_lookup, room, foreign_room, lookup, lookup]))
            self.assertEqual(len(rows), 14)
            self.assertEqual(rows[0][9], 'stored sleep')
            self.assertEqual(source, f'{room}\n{lookup}')

    def test_wrong_name_and_other_namespaces_are_missing_lookup(self):
        with tempfile.TemporaryDirectory() as folder:
            base = pathlib.Path(folder)
            own = base / 'data/user/0/com.withings.wiscale2/databases'
            room, _ = make_room(own / 'room-healthmate')
            candidates = [make_lookup(own / name) for name in
                          ['withings-scale', 'Withings-WiScale-wal', 'Withings-WiScale.bak']]
            candidates += [make_lookup(base / name / 'Withings-WiScale') for name in
                           ['data/user_de/0/com.withings.wiscale2/databases',
                            'data/user/10/com.withings.wiscale2/databases',
                            'otherroot/data/user/0/com.withings.wiscale2/databases',
                            'data/data/com.withings.wiscale2/databases',
                            'data/user/0/com.other.app/databases']]
            (own / 'Withings-WiScale').mkdir()
            with patch('scripts.artifacts.WithingsHealthMate.logfunc'):
                _, rows, source = healthmate_trackings.__wrapped__(Context(folder, [room, *candidates]))
            self.assertEqual(source, str(room))
            self.assertTrue(all(r[9] == '' for r in rows))
            self.assertEqual(rows[0][11], 'missing-lookup')
            self.assertEqual(rows[6][11], 'missing-category-ID')

    def test_schema_and_corrupt_lookup_retain_track_rows(self):
        for bad_schema, corrupt, expected in [(True, False, 'unsupported-lookup-schema'),
                                             (False, True, 'unreadable-lookup')]:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as folder:
                parent = pathlib.Path(folder) / 'data/data/com.withings.wiscale2/databases'
                room, _ = make_room(parent / 'room-healthmate')
                lookup = make_lookup(parent / 'Withings-WiScale', bad_schema=bad_schema, corrupt=corrupt)
                with patch('scripts.artifacts.WithingsHealthMate.logfunc'):
                    _, rows, source = healthmate_trackings.__wrapped__(Context(folder, [room, lookup]))
                self.assertEqual(len(rows), 14)
                self.assertEqual(rows[0][11], expected)
                self.assertEqual(source, str(room))

    def test_exposed_lookup_state_ambiguity_and_physical_mismatch_retain_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            base = pathlib.Path(folder)
            parent = base / 'data/user/0/com.withings.wiscale2/databases'
            room, _ = make_room(parent / 'room-healthmate')
            lookup = make_lookup(parent / 'Withings-WiScale')
            alternate = make_lookup(base / 'alternate/Withings-WiScale', [(37, 'different state')])
            relative = str(lookup.relative_to(base))
            overrides = {str(alternate): relative}
            for files in [[room, lookup, alternate], [room, alternate]]:
                with patch('scripts.artifacts.WithingsHealthMate.logfunc'):
                    _, rows, source = healthmate_trackings.__wrapped__(Context(folder, files, overrides))
                self.assertEqual(rows[0][8], 37)
                self.assertEqual(rows[0][9:], ('', '{"raw":0}', 'ambiguous-lookup'))
                self.assertEqual(source, str(room))

    def test_lookup_reads_own_wal_without_changing_main_or_wal(self):
        with tempfile.TemporaryDirectory() as folder:
            parent = pathlib.Path(folder) / 'data/data/com.withings.wiscale2/databases'
            room, _ = make_room(parent / 'room-healthmate')
            lookup = make_lookup(parent / 'Withings-WiScale', [])
            writer = sqlite3.connect(lookup)
            try:
                writer.execute('PRAGMA journal_mode=WAL')
                writer.execute('INSERT INTO activityCategory VALUES (?,?)', (37, 'name in own WAL'))
                writer.commit()
                state_paths = [lookup, pathlib.Path(str(lookup) + '-wal')]
                hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in state_paths]
                with patch('scripts.artifacts.WithingsHealthMate.logfunc'):
                    _, rows, source = healthmate_trackings.__wrapped__(Context(folder, [room, lookup]))
                self.assertEqual(rows[0][9], 'name in own WAL')
                self.assertEqual(source, f'{room}\n{lookup}')
                self.assertEqual([hashlib.sha256(path.read_bytes()).hexdigest() for path in state_paths],
                                 hashes)
            finally:
                writer.close()

    def test_empty_successful_lookup_contributes_source(self):
        with tempfile.TemporaryDirectory() as folder:
            parent = pathlib.Path(folder) / 'data/data/com.withings.wiscale2/databases'
            room, _ = make_room(parent / 'room-healthmate')
            lookup = make_lookup(parent / 'Withings-WiScale', [])
            with patch('scripts.artifacts.WithingsHealthMate.logfunc'):
                _, rows, source = healthmate_trackings.__wrapped__(Context(folder, [room, lookup]))
            self.assertEqual(rows[0][11], 'category-not-listed')
            self.assertEqual(source, f'{room}\n{lookup}')


if __name__ == '__main__':
    unittest.main()
