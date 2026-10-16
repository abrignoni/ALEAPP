"""Media types preserve unknown domains, duplicates, and evidence sources."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from scripts.artifacts import FilesByGoogle as files_google
from admin.test.scripts.test_history_doclist_all_sources import Context

TYPES = (None, '', 0, 1, 2, 3, 6, 4, 5, 99, -1, 'unknown')
FIELDS = ('file_date_modified_ms', 'root_path', 'root_relative_file_path', 'file_name',
          'size', 'mime_type', 'media_type', 'uri', 'is_hidden', 'title', 'parent_folder_name')


def create_media_fixture(root, missing=False):
    root = Path(root)
    files = []
    for user in [0, 10]:
        target = root/f'A/data/user/{user}/com.google.android.apps.nbu.files/databases/files_master_database'
        target.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(target)
        fields = [f for f in FIELDS if not (missing and f == 'media_type')]
        db.execute('CREATE TABLE files_master_table ('+','.join(fields)+')')
        values = [*TYPES, TYPES[-1]] if user == 0 else [-2]
        for index, media_type in enumerate(values):
            # Repeat the last record exactly, not just its media-type domain.
            index = 11 if index == 12 else index
            row = dict(zip(FIELDS, (1700000000000 if index%2 else None, '/storage/emulated/0',
                                   f'folder/{index}.file', f'{index} <file>', 5, 'application/data',
                                   media_type, f'uri:{index}', index%2, '<title>', 'folder')))
            db.execute('INSERT INTO files_master_table VALUES ('+','.join('?' for _ in fields)+')',
                       [row[f] for f in fields])
        db.commit()
        db.close()
        files.append(target)
        target.with_name(target.name+'-journal').write_bytes(b'')
    return files


class TestFilesGoogleRawMediaType(unittest.TestCase):
    def test_unknown_null_duplicate_and_distinct_user_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_media_fixture(directory)
            headers, rows, sources = files_google.fbg_master.__wrapped__(Context(directory, files))
            self.assertEqual(len(rows), 14)
            index = headers.index('Media Type (as stored)')
            self.assertEqual([r[index] for r in rows], [*TYPES, 'unknown', -2])
            self.assertEqual(rows[-3], rows[-2])
            self.assertEqual(len(sources.splitlines()), 2)
            self.assertTrue(all(Path(directory, row[-1]).is_file() for row in rows))
            self.assertEqual(rows[-1][-1], str(files[-1].relative_to(directory)))
            self.assertIsNone(rows[0][0])
            self.assertEqual(rows[1][0].timestamp(), 1700000000)
            self.assertEqual(rows[1][8], 'Yes')
            self.assertEqual(rows[0][8], '')

    def test_missing_column_remains_explicit_schema_error(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_media_fixture(directory, missing=True)
            connection = files_google.open_sqlite_db_readonly(str(files[0]))
            try:
                with patch.object(files_google, 'open_sqlite_db_readonly', return_value=connection):
                    with self.assertRaisesRegex(sqlite3.OperationalError, 'no such column: media_type'):
                        files_google.fbg_master.__wrapped__(Context(directory, files))
            finally:
                connection.close()


if __name__ == '__main__':
    unittest.main()
