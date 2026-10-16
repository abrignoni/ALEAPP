"""Actual SQLite flag fidelity and unchanged native library columns."""
import hashlib
import itertools
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from scripts.artifacts import easyVoiceRecorder as artifact

PACKAGE = 'com.coffeebeanventures.easyvoicerecorder'
FLAGS = [None, 0, 1, -1, 2, 0.5, '', '0', 'false', 'unknown', b'', b'0', b'\xff', 0]
URI = 'content://authority/tree/primary%3ARecordings/document/primary%3ARecordings%2Fnote.m4a'


class Context:
    def __init__(self, root, files):
        self.root, self.files = Path(root), list(map(str, files))

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in Path(root).rglob('*') if p.is_file()}


def create_database(path, flags=None, wal=False, integer_affinity=False):
    flags = FLAGS if flags is None else flags
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    if wal:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA wal_autocheckpoint=0')
    flag_column = 'should_be_stickied INTEGER' if integer_affinity else 'should_be_stickied'
    db.execute('CREATE TABLE files(path,length_in_seconds,' + flag_column + ',_id)')
    for index, value in enumerate(flags):
        db.execute('INSERT INTO files VALUES(?,?,?,?)',
                   (URI, None if index == 0 else -1 if index == 1 else index,
                    value, index // 2))
    db.commit()
    if wal:
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        db.execute('INSERT INTO files VALUES(?,?,?,?)', (URI, 1, None, 99))
        db.execute('INSERT INTO files VALUES(?,?,?,?)', (URI, 1, 0, 99))
        db.execute('INSERT INTO files VALUES(?,?,?,?)', (URI, 1, 'unknown', 99))
        db.commit()
    return db


def direct_rows(root, path):
    db = sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True)
    try:
        records = db.execute('SELECT path,length_in_seconds,should_be_stickied,_id '
                             'FROM files ORDER BY _id').fetchall()
    finally:
        db.close()
    # The fixture URI decodes to these known values, independently of _saf_parts.
    return [('note.m4a', 'Recordings', duration if duration is not None and duration >= 0 else '',
             flag, uri, row_id, str(Path(path).relative_to(root)))
            for uri, duration, flag, row_id in records]


class TestEasyVoiceStoredFlag(unittest.TestCase):
    def test_all_sqlite_storage_classes_and_false_value_distinctions(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/'data/data'/PACKAGE/'databases/evr.db'
            create_database(path).close()
            before = hashes(root)
            headers, rows, source = artifact.easyvoicerecorder_library.__wrapped__(
                Context(root, [path]))
            expected = direct_rows(root, path)
            self.assertEqual(rows, expected)
            self.assertEqual([[type(v) for v in r] for r in rows],
                             [[type(v) for v in r] for r in expected])
            self.assertEqual(len(headers), 7)
            self.assertEqual(headers[3], 'should_be_stickied (as stored)')
            self.assertEqual(source, str(path))
            self.assertEqual([r[3] for r in rows], FLAGS)
            self.assertEqual(hashes(root), before)

    def test_genuine_integer_affinity_preserves_actual_stored_values(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/'data/data'/PACKAGE/'databases/evr.db'
            create_database(path, integer_affinity=True).close()
            _, rows, _ = artifact.easyvoicerecorder_library.__wrapped__(Context(root, [path]))
            expected = direct_rows(root, path)
            self.assertEqual(rows, expected)
            self.assertEqual([[type(v) for v in r] for r in rows],
                             [[type(v) for v in r] for r in expected])
            # Numeric text is converted by SQLite INTEGER affinity before the query.
            self.assertIsInstance(rows[7][3], int)
            self.assertEqual(rows[7][3], 0)
            self.assertIsInstance(rows[5][3], float)
            self.assertEqual(rows[12][3], b'\xff')

    def test_live_wal_rows_and_repeats(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            live = root/'build/evr.db'
            writer = create_database(live, wal=True)
            try:
                # Read an operational copy of the coherent live main and sidecars.
                dest = root/'operational/data/data'/PACKAGE/'databases/evr.db'
                dest.parent.mkdir(parents=True)
                for suffix in ['', '-wal', '-shm']:
                    shutil.copy2(str(live)+suffix, str(dest)+suffix)
                    Path(str(dest)+suffix).chmod(0o444)
                initial = hashes(dest.parent)
                _, rows, _ = artifact.easyvoicerecorder_library.__wrapped__(
                    Context(root/'operational', [dest]))
                self.assertEqual(rows, direct_rows(root/'operational', dest))
                self.assertEqual([r[3] for r in rows[-3:]], [None, 0, 'unknown'])
                self.assertEqual(hashes(dest.parent), initial)
            finally:
                writer.close()

    def test_selected_alias_policy_and_multiple_sources(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            paths = [root/p/PACKAGE/'databases/evr.db' for p in
                     ['data/data', 'data/user/0', 'data_mirror/data_ce/null/0', 'data/user/10']]
            for path, value in zip(paths, [0, 1, 0, 'unknown']):
                create_database(path, [value]).close()
            initial = hashes(root)
            for order in itertools.permutations(paths):
                context = Context(root, order)
                selected = artifact._files(context, artifact.DB_SUFFIX)  # pylint: disable=protected-access
                self.assertEqual(set(selected), {str(paths[0]), str(paths[3])})
                _, rows, source = artifact.easyvoicerecorder_library.__wrapped__(context)
                self.assertEqual(rows, [r for p in selected for r in direct_rows(root, p)])
                self.assertEqual(source.splitlines(), selected)
            self.assertEqual(hashes(root), initial)
