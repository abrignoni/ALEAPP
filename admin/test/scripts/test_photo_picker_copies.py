"""Photo Picker Cached Copies on a synthetic tree (values invented for the test)."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import photoPickerCopies as parser  # noqa: E402

LOCAL = 'com.android.providers.media.photopicker'
CLOUD = 'com.google.android.apps.photos.cloudpicker'
MODULE = 'com.google.android.providers.media.module'


def _db(path, script, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.executescript(script)
    for sql, values in rows:
        db.execute(sql, values)
    db.commit()
    db.close()
    return str(path)


def fixture(root):
    paths = []
    files = [
        f'data/media/0/.transforms/synthetic/picker_get_content/0/{LOCAL}/media/11.jpg',
        f'mnt/pass_through/10/emulated/0/.transforms/synthetic/picker_get_content/0/{LOCAL}/media/11.jpg',
        f'data/media/0/.transforms/synthetic/picker/0/{LOCAL}/media/12.jpg',
        f'data/media/0/.transforms/synthetic/picker/0/{LOCAL}/media/13.jpg',
        f'data/media/0/.transforms/synthetic/picker_get_content/0/{CLOUD}/media/abc-1_all_2.jpg',
    ]
    for relative in files:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'\xff\xd8\xff' + b'x' * 20)
        paths.append(str(path))
    files_table = ('CREATE TABLE files(_id INTEGER PRIMARY KEY, _display_name, _data, date_added, '
                   'date_modified, datetaken, owner_package_name, _size);'
                   'CREATE TABLE deleted_media(_id INTEGER PRIMARY KEY, old_id INTEGER UNIQUE, '
                   'generation_modified INTEGER);')
    paths.append(_db(root / f'data/data/{MODULE}/databases/external.db', files_table, [
        ('INSERT INTO files VALUES(11,"one.jpg","/storage/emulated/0/DCIM/one.jpg",1700000000,'
         '1700000000,1699999000000,"com.example.camera",23)', ()),
        ('INSERT INTO deleted_media VALUES(1,12,5)', ()),
    ]))
    # user 10 has an unrelated row with id 13; the user 0 copy 13 must not join to it
    paths.append(_db(root / f'data/user/10/{MODULE}/databases/external.db', files_table, [
        ('INSERT INTO files VALUES(13,"other.jpg","/storage/emulated/10/x.jpg",1,1,NULL,NULL,9)', ()),
    ]))
    paths.append(_db(root / f'data/data/{MODULE}/databases/picker.db',
                     'CREATE TABLE media(_id INTEGER PRIMARY KEY, local_id, cloud_id, '
                     'date_taken_ms, size_bytes, mime_type);', [
                         ('INSERT INTO media VALUES(1,NULL,"abc-1_all_2",1700000500000,23,"image/jpeg")', ()),
                     ]))
    return paths


def context(root, paths):
    return SimpleNamespace(get_files_found=lambda: paths,
                           get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))


class PhotoPickerCopiesTest(unittest.TestCase):
    def test_joins_and_views(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            paths = fixture(root)
            with patch.object(parser, 'check_in_media', side_effect=lambda p, *_: 'media'), \
                    patch.object(parser.Context, 'get_seeker', return_value=None):
                headers, rows, source = parser.get_photo_picker_copies.__wrapped__(context(root, paths))
        self.assertTrue(all(len(r) == len(headers) for r in rows))
        by_id = {r[9]: r for r in rows}
        self.assertEqual(sorted(by_id), ['11', '12', '13', 'abc-1_all_2'])  # two views of 11 collapse
        self.assertEqual(by_id['11'][17], 'external.db files')
        self.assertEqual(by_id['11'][13], 'one.jpg')
        self.assertEqual(by_id['12'][17], 'external.db deleted_media only (no files row)')
        self.assertEqual(by_id['12'][13], '')
        self.assertEqual(by_id['13'][17], '')                                # user 10 row not used
        self.assertEqual(by_id['abc-1_all_2'][17], 'picker.db media')
        self.assertEqual(by_id['abc-1_all_2'][12], 23)
        self.assertEqual([r[0] for r in rows], [''] * 4)                     # no recorded times
        self.assertEqual(by_id['11'][15], 'not searched')                 # no seeker in the test
        self.assertEqual(by_id['11'][5], '')
        self.assertNotIn('/data/user/10/', source)

    def test_copy_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            zero = root / 'z.jpg'
            zero.write_bytes(bytes(64))
            empty = root / 'e.jpg'
            empty.write_bytes(b'')
            self.assertEqual(parser._content(str(zero)), 'all zero bytes')  # pylint: disable=protected-access
            self.assertEqual(parser._content(str(empty)), 'empty')  # pylint: disable=protected-access


if __name__ == '__main__':
    unittest.main()
