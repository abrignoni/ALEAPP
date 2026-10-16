"""Retain cloud-cache flags without assigning completion semantics."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import galleryVault


COLUMNS = ('file_add_time_utc', 'file_org_create_time_utc', 'name', 'file_uuid',
           'mime_type', 'size', 'image_width', 'image_height', 'parent_folder_id',
           'is_complete', 'has_thumb', 'cloud_file_storage_key', 'file_encryption_key',
           'move_to_recycle_bin_time_utc', 'file_content_hash', 'cloud_drive_id')


def make_db(path, affinity='', wal=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    if wal:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA wal_autocheckpoint=0')
    db.execute('CREATE TABLE cloud_files (' + ','.join(
        name + (' ' + affinity if name == 'is_complete' else '') for name in COLUMNS) + ')')
    db.execute('CREATE TABLE cloud_folders(entry_id,name,parent_folder_id)')
    db.commit()
    if wal:
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    return db


def parse(paths):
    context = SimpleNamespace(get_files_found=lambda: paths)
    return galleryVault.galleryvault_cloud_files.__wrapped__(context)


def insert(db, value):
    row = (1704164645000, 1704164645000, 'same', 'id', 'opaque', 0, 0, 0, 0,
           value, '0', 'storage', b'\x00\xff', 0, 'hash', 'drive')
    db.execute('INSERT INTO cloud_files VALUES (' + ','.join('?' for _ in row) + ')', row)
    db.commit()


class TestGalleryVaultCloudComplete(unittest.TestCase):
    def test_raw_storage_classes_affinity_and_repeated_rows(self):
        values = [None, 0, 1, -1, 1.25, '0', '', 'unknown', b'\xff\x00', b'',
                  2 ** 63 - 1, -(2 ** 63), 'unknown']
        for affinity in ['', 'TEXT', 'INTEGER', 'REAL']:
            with self.subTest(affinity=affinity), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'cloud_cache.db'
                db = make_db(path, affinity)
                try:
                    for value in values:
                        insert(db, value)
                    expected = db.execute('SELECT is_complete FROM cloud_files').fetchall()
                    _, rows, source = parse([path])
                    self.assertEqual([row[8] for row in rows], [row[0] for row in expected])
                    self.assertEqual([type(row[8]) for row in rows],
                                     [type(row[0]) for row in expected])
                    self.assertEqual(len(rows), len(values))
                    self.assertEqual(source, path)
                    self.assertTrue(all(len(row) == 15 for row in rows))
                    self.assertTrue(all(row[9] == 'Yes' for row in rows))
                finally:
                    db.close()

    def test_wal_rows_and_current_first_main_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / 'first/cloud_cache.db'
            second = Path(tmp) / 'second/cloud_cache.db'
            writer = make_db(first, wal=True)
            empty = make_db(second)
            try:
                insert(writer, 0)
                control = sqlite3.connect(first.as_uri() + '?immutable=1', uri=True)
                try:
                    self.assertEqual(control.execute('SELECT COUNT(*) FROM cloud_files').fetchone()[0], 0)
                finally:
                    control.close()
                _, rows, source = parse([first.with_name('cloud_cache.db-wal'), first, second])
                self.assertEqual([row[8] for row in rows], [0])
                self.assertEqual(source, first)
                _, rows, source = parse([second, first])
                self.assertEqual(rows, [])
                self.assertEqual(source, second)
            finally:
                writer.close()
                empty.close()


if __name__ == '__main__':
    unittest.main()
