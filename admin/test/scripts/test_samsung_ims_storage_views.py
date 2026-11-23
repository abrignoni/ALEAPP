"""Credential and device encrypted copies are different files, and a user folder is read in every layout."""
# pylint: disable=protected-access
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import samsungImsService

XML = '<?xml version="1.0"?><map><string name="{key}">sip:{user}@example.test</string></map>'


def subscriber_rows(relative_paths):
    with tempfile.TemporaryDirectory() as folder:
        root = pathlib.Path(folder)
        files = []
        for number, relative in enumerate(relative_paths):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(XML.format(key=f'31041000000000{number}', user=f'user{number}'))
            files.append(str(path))
        context = SimpleNamespace(get_files_found=lambda: files,
                                  get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))
        _headers, rows, _source = samsungImsService.samsungImsSubscriber.__wrapped__(context)
    return rows


class StorageViews(unittest.TestCase):
    def test_credential_and_device_copies_are_both_read(self):
        rows = subscriber_rows(['data/user/0/com.sec.imsservice/shared_prefs/saved_impu.xml',
                                'data/user_de/0/com.sec.imsservice/shared_prefs/saved_impu.xml'])
        self.assertEqual(len(rows), 2)

    def test_views_of_one_file_are_read_once(self):
        rows = subscriber_rows(['data/data/com.sec.imsservice/shared_prefs/saved_impu.xml',
                                'data/user/0/com.sec.imsservice/shared_prefs/saved_impu.xml'])
        self.assertEqual(len(rows), 1)

    def test_two_users_are_both_read(self):
        rows = subscriber_rows(['data/user_de/0/com.sec.imsservice/shared_prefs/saved_impu.xml',
                                'data/user_de/150/com.sec.imsservice/shared_prefs/saved_impu.xml'])
        self.assertEqual(len(rows), 2)


class AndroidUser(unittest.TestCase):
    def test_user_folder_in_each_layout(self):
        for path, user in (('/data/user_de/150/com.sec.imsservice/files/a.log', '150'),
                           ('/data/user/10/com.sec.imsservice/files/a.log', '10'),
                           ('/userdata/user_de/150/com.sec.imsservice/files/a.log', '150'),
                           ('/userdata/user/150/com.sec.imsservice/files/a.log', '150'),
                           ('/data_mirror/data_de/null/150/com.sec.imsservice/files/a.log', '150')):
            self.assertEqual(samsungImsService._android_user(path), user, path)


if __name__ == '__main__':
    unittest.main()
