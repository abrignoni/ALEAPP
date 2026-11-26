"""The schema's default creation_date is not shown as a real Created time, and a media row from an older
schema without the size and view count columns is still reported. No value comes from evidence: the
dates are the schema default and that default plus one millisecond, and the rest are made up."""
# pylint: disable=protected-access
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import PrivatePhotoVault as ppv


class DefaultDate(unittest.TestCase):
    def test_the_schema_default_is_blank(self):
        self.assertIsNone(ppv._iso_to_utc('2021-01-01T01:00:00.000Z'))

    def test_another_time_is_converted(self):
        self.assertEqual(ppv._iso_to_utc('2021-01-01T01:00:00.001Z').isoformat(), '2021-01-01T01:00:00.001000+00:00')



class OlderSchema(unittest.TestCase):
    def test_media_rows_without_size_and_view_columns_are_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / 'data/data/com.enchantedcloud.photovault/databases/ppv.db'
            path.parent.mkdir(parents=True)
            db = sqlite3.connect(path)
            db.execute('CREATE TABLE MediaFile (creation_date TEXT, bucket_id TEXT, file_path TEXT, thumbnail_path TEXT, '
                       'mime_type TEXT, is_favourite INTEGER, is_deleted INTEGER, encryption_key TEXT, local_iv TEXT)')
            db.execute("INSERT INTO MediaFile VALUES ('2024-01-01T00:00:00.000+00:00', 'albums', 'f', 't', 'image/jpeg', 0, 0, 'k', 'iv')")
            db.commit()
            db.close()
            context = SimpleNamespace(get_files_found=lambda: [str(path)],
                                      get_relative_path=lambda p: str(pathlib.Path(p).relative_to(folder)))
            headers, rows, _source = ppv.private_photo_vault_media.__wrapped__(context)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        self.assertEqual(len(rows), 1)
        row = dict(zip(names, rows[0]))
        self.assertEqual((row['Image Width'], row['Image Height'], row['View Count']), (None, None, None))
        self.assertEqual(row['MIME Type'], 'image/jpeg')


if __name__ == '__main__':
    unittest.main()
