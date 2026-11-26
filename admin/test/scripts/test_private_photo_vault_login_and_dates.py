"""Private Photo Vault login records are reported, and media rows carry the stored deletion,
trash, favourite and upload dates. All values here are made up."""
# pylint: disable=protected-access
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import PrivatePhotoVault as ppv


def run(artifact):
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / 'data/data/com.enchantedcloud.photovault/databases/ppv.db'
        path.parent.mkdir(parents=True)
        db = sqlite3.connect(path)
        db.execute('CREATE TABLE LoginRecord (uid TEXT NOT NULL, orig_file_path TEXT, date TEXT, type TEXT NOT NULL, '
                   'latitude REAL, longitude REAL, PRIMARY KEY(uid))')
        db.execute("INSERT INTO LoginRecord VALUES ('u1', '/made/up.jpg', '2024-05-01T10:00:00.000Z', 'kind', 1.5, -2.5)")
        db.execute('CREATE TABLE MediaFile (creation_date TEXT, bucket_id TEXT, file_path TEXT, thumbnail_path TEXT, '
                   'mime_type TEXT, image_width INTEGER, image_height INTEGER, is_favourite INTEGER, is_deleted INTEGER, '
                   'view_count INTEGER, encryption_key TEXT, local_iv TEXT, deleted_time TEXT, trashed_date TEXT, '
                   'favourite_date TEXT, uploaded_date TEXT)')
        db.execute("INSERT INTO MediaFile VALUES ('2024-01-01T00:00:00.000+00:00', 'albums', 'f', 't', 'image/jpeg', 1, 2, "
                   "1, 1, 0, 'k', 'iv', 'D1', 'T1', 'F1', 'U1')")
        db.commit()
        db.close()
        context = SimpleNamespace(get_files_found=lambda: [str(path)],
                                  get_relative_path=lambda p: str(pathlib.Path(p).relative_to(folder)))
        headers, rows, _source = getattr(ppv, artifact).__wrapped__(context)
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return [dict(zip(names, row)) for row in rows], headers


class LoginRecords(unittest.TestCase):
    def test_a_login_record_is_reported(self):
        rows, headers = run('private_photo_vault_login_records')
        row = rows[0]
        self.assertEqual(row['Date'].isoformat(), '2024-05-01T10:00:00+00:00')
        self.assertEqual(row['Date (as stored)'], '2024-05-01T10:00:00.000Z')
        self.assertEqual(row['Type (as stored)'], 'kind')
        self.assertEqual((row['Latitude'], row['Longitude']), (1.5, -2.5))
        self.assertEqual(row['Original File Path (as stored)'], '/made/up.jpg')
        self.assertIn(('Latitude', 'latitude'), headers)


class MediaDates(unittest.TestCase):
    def test_the_four_dates_are_reported_as_stored(self):
        rows, _headers = run('private_photo_vault_media')
        row = rows[0]
        self.assertEqual((row['Deleted Time (As Stored)'], row['Trashed Date (As Stored)'],
                          row['Favourite Date (As Stored)'], row['Uploaded Date (As Stored)']), ('D1', 'T1', 'F1', 'U1'))


    def test_the_dates_follow_the_creation_date(self):
        _rows, headers = run('private_photo_vault_media')
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        self.assertEqual(names[2:6], ['Deleted Time (As Stored)', 'Trashed Date (As Stored)',
                                      'Favourite Date (As Stored)', 'Uploaded Date (As Stored)'])


class LoginDateDefault(unittest.TestCase):
    def test_a_login_date_equal_to_the_other_tables_default_is_still_converted(self):
        self.assertIsNotNone(ppv._iso_to_utc('2021-01-01T01:00:00.000Z', skip_schema_default=False))


if __name__ == '__main__':
    unittest.main()
