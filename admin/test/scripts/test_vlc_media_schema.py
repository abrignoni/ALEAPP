"""Optional VLC columns must not hide media from older supported schemas."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.artifacts.vlcMedia import get_vlcMedia  # pylint: disable=wrong-import-position


class Context:
    def __init__(self, path):
        self.path = str(path)

    def get_files_found(self):
        return [self.path]

    def get_relative_path(self, path):
        return pathlib.Path(path).name


class TestVlcOptionalColumns(unittest.TestCase):
    def parse(self, extra_columns):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / 'vlc_media.db'
            with sqlite3.connect(path) as db:
                db.execute('CREATE TABLE Folder(id_folder INTEGER, path TEXT)')
                db.execute('INSERT INTO Folder VALUES(1, "file:///storage/media")')
                columns = ('insertion_date INTEGER, last_played_date INTEGER, filename TEXT, '
                           'folder_id INTEGER, is_favorite INTEGER, play_count INTEGER, '
                           'last_time INTEGER, duration INTEGER, type INTEGER, title TEXT')
                for column in extra_columns:
                    columns += ', ' + column + ' INTEGER'
                db.execute('CREATE TABLE Media(' + columns + ')')
                values = [1700000000, 1700000001, 'sample.mp4', 1, 0, 1, 1234, 5000, 1, 'sample']
                values += [extra_columns[column] for column in extra_columns]
                db.execute('INSERT INTO Media VALUES(' + ','.join('?' for _ in values) + ')', values)
            return get_vlcMedia.__wrapped__(Context(path))

    def test_old_schema_retains_the_media_row(self):
        headers, rows, _ = self.parse({})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][2], 'sample.mp4')
        self.assertEqual(rows[0][10:12], (None, None))
        self.assertEqual(len(headers), len(rows[0]))

    def test_new_schema_retains_optional_values(self):
        _, rows, _ = self.parse({'last_position': 7, 'import_type': 2})
        self.assertEqual(rows[0][10:12], (7, 2))

    def test_partial_schema_retains_the_available_value(self):
        _, rows, _ = self.parse({'import_type': 2})
        self.assertEqual(rows[0][10:12], (None, 2))


if __name__ == '__main__':
    unittest.main()
