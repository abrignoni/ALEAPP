"""WhatsApp media with no file_path entry: rollback references, missing files, bad times and repeated copies."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.artifacts import whatsAppUnreferencedMedia as module  # noqa: E402

MEDIA = 'Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images/'


class UnreferencedMedia(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = pathlib.Path(temporary.name)
        self.files = []
        self.infos = {}
        patcher = mock.patch.object(module, 'check_in_media', side_effect=lambda path, name=None: 'ref')
        patcher.start()
        self.addCleanup(patcher.stop)

    def database(self, relative, *paths):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(path)
        con.execute('CREATE TABLE message_media (message_row_id INTEGER, file_path TEXT)')
        con.executemany('INSERT INTO message_media VALUES (?, ?)', [(i, p) for i, p in enumerate(paths)])
        con.commit()
        con.close()
        self.files.append(str(path))

    def media(self, relative, content=b'photo'):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        self.files.append(str(path))
        return str(path)

    def rows(self):
        context = SimpleNamespace(
            get_files_found=lambda: list(self.files),
            get_relative_path=lambda path: str(pathlib.Path(path).relative_to(self.root)),
            get_seeker=lambda: SimpleNamespace(file_infos=self.infos))
        headers, rows, _source = module.whatsapp_unreferenced_media.__wrapped__(context)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        return [dict(zip(names, row)) for row in rows]

    def test_a_rollback_copy_that_names_the_file_counts_for_its_user(self):
        self.database('data/data/com.whatsapp/databases/msgstore.db', 'Media/WhatsApp Images/other.jpg')
        self.media('data/media/0/' + MEDIA + 'a.jpg')
        self.assertEqual(len(self.rows()), 1)
        self.database('data/misc_ce/0/rollback/7/com.whatsapp/databases/msgstore.db', 'Media/WhatsApp Images/a.jpg')
        self.assertEqual(self.rows(), [])

    def test_a_path_with_no_file_behind_it_is_skipped(self):
        self.database('data/data/com.whatsapp/databases/msgstore.db')
        self.files.append(str(self.root / ('data/media/0/' + MEDIA + 'dangling.jpg')))
        self.media('data/media/0/' + MEDIA + 'real.jpg')
        self.assertEqual([row['File Name'] for row in self.rows()], ['real.jpg'])

    def test_an_out_of_range_time_is_left_blank(self):
        self.database('data/data/com.whatsapp/databases/msgstore.db')
        path = self.media('data/media/0/' + MEDIA + 'a.jpg')
        self.infos[path] = SimpleNamespace(times=SimpleNamespace(modified=1e20, modified_no_zone=None))
        self.assertEqual([row['File Modified'] for row in self.rows()], [''])

    def test_each_distinct_copy_is_shown_once(self):
        self.database('data/data/com.whatsapp/databases/msgstore.db')
        self.media('data/media/0/' + MEDIA + 'a.jpg', b'first')
        self.media('storage/emulated/0/' + MEDIA + 'a.jpg', b'second')
        self.media('mnt/pass_through/0/emulated/0/' + MEDIA + 'a.jpg', b'second')
        self.assertEqual(len(self.rows()), 2)


if __name__ == '__main__':
    unittest.main()
