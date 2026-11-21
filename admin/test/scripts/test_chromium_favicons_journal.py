"""How Chromium Favicons reads a database that has a pending rollback journal."""
import hashlib
import os
import shutil
import sqlite3
import struct
import tempfile
import unittest
from unittest import mock

from scripts.artifacts.chromiumFavicons import _read_database

_LOG = 'scripts.artifacts.chromiumFavicons.logfunc'


def _read_values(db):
    return sorted(row[0] for row in db.execute('SELECT value FROM items'))


def _digest(path):
    with open(path, 'rb') as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _build(path, rows=400):
    db = sqlite3.connect(path)
    db.execute('PRAGMA journal_mode=DELETE')
    db.execute('CREATE TABLE items (id INTEGER PRIMARY KEY, value TEXT)')
    db.executemany('INSERT INTO items (value) VALUES (?)',
                   [(f'old-{n:05}' + 'x' * 200,) for n in range(rows)])
    db.commit()
    return db


def _capture_interrupted_write(db, path, target):
    """Copy the database and its hot journal while a spilled write is open."""
    db.isolation_level = None
    db.execute('PRAGMA cache_size=1')
    db.execute('BEGIN IMMEDIATE')
    db.execute("UPDATE items SET value = 'new-' || id || substr(value, 5)")
    shutil.copyfile(path, target)
    shutil.copyfile(f'{path}-journal', f'{target}-journal')
    db.execute('COMMIT')


class ReadDatabaseWithJournal(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.folder)
        self.source = os.path.join(self.folder, 'source')
        self.path = os.path.join(self.folder, 'Favicons')
        self.journal = f'{self.path}-journal'

    def test_sound_rollback_is_used_and_evidence_is_unchanged(self):
        db = _build(self.source)
        _capture_interrupted_write(db, self.source, self.path)
        db.close()
        before = _digest(self.path), _digest(self.journal)
        with mock.patch(_LOG) as log:
            values, journal = _read_database(self.path, _read_values, 'Favicons')
        self.assertIn('rolled it back', log.call_args.args[0])
        self.assertEqual(journal, self.journal)
        self.assertEqual(len(values), 400)
        self.assertTrue(all(value.startswith('old-') for value in values))
        self.assertEqual((_digest(self.path), _digest(self.journal)), before)
        self.assertEqual(sorted(os.listdir(self.folder)),
                         sorted(['source', 'Favicons', 'Favicons-journal']))

    def test_stale_journal_that_damages_the_database_falls_back_to_as_found(self):
        db = _build(self.source)
        stale = os.path.join(self.folder, 'stale')
        _capture_interrupted_write(db, self.source, stale)
        db.execute('DELETE FROM items WHERE id % 2 = 0')
        db.execute('VACUUM')
        db.execute("INSERT INTO items (value) VALUES ('kept-after-the-journal')")
        db.close()
        shutil.copyfile(self.source, self.path)
        shutil.copyfile(f'{stale}-journal', self.journal)

        probe = os.path.join(self.folder, 'probe')
        shutil.copyfile(self.path, probe)
        shutil.copyfile(self.journal, f'{probe}-journal')
        check = sqlite3.connect(probe)
        try:
            damaged = check.execute('PRAGMA integrity_check(1)').fetchone()[0] != 'ok'
        except sqlite3.DatabaseError:
            damaged = True
        check.close()
        for name in (probe, f'{probe}-journal'):
            if os.path.exists(name):
                os.remove(name)
        self.assertTrue(damaged, 'the fixture must make rollback damage the database')

        before = _digest(self.path), _digest(self.journal)
        with mock.patch(_LOG) as log:
            values, journal = _read_database(self.path, _read_values, 'Favicons')
        self.assertIn('read as found', log.call_args.args[0])
        self.assertIsNone(journal)
        self.assertIn('kept-after-the-journal', values)
        self.assertEqual((_digest(self.path), _digest(self.journal)), before)

    def test_journal_sqlite_does_not_play_back_is_not_called_a_rollback(self):
        db = _build(self.source)
        _capture_interrupted_write(db, self.source, self.path)
        db.close()
        name = b'/nonexistent/super-journal'
        with open(self.journal, 'ab') as handle:
            handle.write(name + struct.pack('>II', len(name), sum(name)))
            handle.write(bytes.fromhex('d9d505f920a163d7'))
        before = _digest(self.path), _digest(self.journal)
        with mock.patch(_LOG) as log:
            values, journal = _read_database(self.path, _read_values, 'Favicons')
        self.assertIn('read as found', log.call_args.args[0])
        self.assertIsNone(journal)
        self.assertTrue(any(value.startswith('new-') for value in values))
        self.assertEqual((_digest(self.path), _digest(self.journal)), before)

    def test_neither_copy_sound_is_refused(self):
        db = _build(self.source)
        _capture_interrupted_write(db, self.source, self.path)
        db.close()
        with open(self.path, 'r+b') as handle:
            handle.seek(4096)
            handle.write(b'\xff' * 8192)
        with open(self.journal, 'r+b') as handle:
            handle.seek(512)
            handle.write(b'\xff' * 4096)
        before = _digest(self.path), _digest(self.journal)
        with self.assertRaisesRegex(sqlite3.DatabaseError, 'neither the rolled-back copy'):
            _read_database(self.path, _read_values, 'Favicons')
        self.assertEqual((_digest(self.path), _digest(self.journal)), before)


if __name__ == '__main__':
    unittest.main()
