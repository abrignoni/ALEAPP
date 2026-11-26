"""A user tag is joined to its file on files.sec_media_id, the link cmh.db's own
files_delete_recommendation_view uses. All values here are made up."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import cmhTags


def user_tag_rows(file_id, sec_media_id, linked_id):
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / 'cmh.db'
        db = sqlite3.connect(path)
        db.execute('CREATE TABLE files (_id INTEGER PRIMARY KEY, sec_media_id INTEGER, datetaken INTEGER, title TEXT, _data TEXT)')
        db.execute('CREATE TABLE usertag (user_tag_id INTEGER PRIMARY KEY, fk_sec_media_id INTEGER, user_tag_data TEXT, timestamp INTEGER)')
        db.execute('INSERT INTO files VALUES (?, ?, 1700000000000, ?, ?)', (file_id, sec_media_id, 'photo', '/storage/photo.jpg'))
        db.execute('INSERT INTO usertag VALUES (1, ?, ?, 1700000000000)', (linked_id, 'tag'))
        db.commit()
        db.close()
        context = SimpleNamespace(get_files_found=lambda: [str(path)])
        headers, rows, _source = cmhTags.cmh_user_tags.__wrapped__(context)
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return [dict(zip(names, row)) for row in rows]


class UserTagLink(unittest.TestCase):
    def test_the_tag_finds_its_file_by_sec_media_id(self):
        row = user_tag_rows(file_id=1, sec_media_id=500, linked_id=500)[0]
        self.assertEqual(row['File Path'], '/storage/photo.jpg')

    def test_a_tag_is_not_joined_on_the_files_row_id(self):
        row = user_tag_rows(file_id=500, sec_media_id=7, linked_id=500)[0]
        self.assertIsNone(row['File Path'])


if __name__ == '__main__':
    unittest.main()
