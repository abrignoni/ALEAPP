"""Empty stored chat identifiers do not discard otherwise parsed messages."""
import datetime
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts.ZangiChats import zangichats  # pylint: disable=wrong-import-position


def make_context(paths):
    return SimpleNamespace(get_files_found=lambda: [str(item) for item in paths],
                           get_relative_path=str)


def make_database(path):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute('CREATE TABLE user_profile(id,first_name,last_name)')
    connection.executemany('INSERT INTO user_profile VALUES(?,?,?)',
                           [(10, 'Chat', 'Name'), (20, 'Sender', ''), (30, 'Receiver', None)])
    connection.execute('CREATE TABLE message(date,chatWith,message_id,msgId,message_msg,extra,msgFrom,msgTo,isIncoming)')
    records = [(1700000000123, 10, 1, 'm1', 'valid', None, 20, 30, 0),
               (1700000001123, '', 2, 'm2', 'empty', '', None, 0, 1),
               (1700000002123, None, 3, 'm3', 'null', None, '', None, 0),
               (1700000003123, 0, 4, 'm4', 'zero', '', 0, '', 1),
               (1700000004123, 999, 5, 'm5', 'missing-profile', None, 20, 30, 1)]
    records.append(records[0])
    connection.executemany('INSERT INTO message VALUES(?,?,?,?,?,?,?,?,?)', records)
    connection.commit()
    connection.close()
    return path, records


class ZangiChatRetentionTest(unittest.TestCase):
    def test_empty_null_chat_and_missing_profiles_keep_raw_ids_and_multiplicity(self):
        with tempfile.TemporaryDirectory() as directory:
            path, records = make_database(pathlib.Path(directory) / 'messages.db')
            context = make_context([path])
            with patch('scripts.artifacts.ZangiChats.check_in_media') as media:
                headers, rows, source = zangichats.__wrapped__(context)
            self.assertEqual(len(headers), 12)
            self.assertEqual(headers[0], ('Timestamp', 'datetime'))
            self.assertEqual(headers[11], 'Source File')
            self.assertTrue(all(row[11] == str(path) for row in rows))
            self.assertEqual(source, str(path))
            self.assertEqual(len(rows), 6)
            self.assertEqual(rows[0], rows[5])
            self.assertEqual([row[6] for row in rows], [10, '', None, 0, 999, 10])
            for row, stored in zip(rows, records):
                self.assertEqual((row[7], row[8], row[10]), (stored[2], stored[6], stored[7]))
                self.assertEqual(row[4], stored[4])
                self.assertIs(type(row[6]), type(stored[1]))
                self.assertEqual(row[0], datetime.datetime.fromtimestamp(stored[0] / 1000,
                                                                        datetime.timezone.utc))
            self.assertEqual([row[3] for row in rows], ['Chat Name', None, None, None, None, 'Chat Name'])
            media.assert_not_called()

    def test_every_message_database_is_read_and_others_are_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory) / 'data' / 'data' / 'com.beint.zangi' / 'databases'
            first, _ = make_database(root / '111.db')
            second, _ = make_database(root / '222.db')
            settings, _ = make_database(root / 'settings.db')
            other = root / 'other.db'
            connection = sqlite3.connect(other)
            connection.execute('CREATE TABLE unrelated(x)')
            connection.commit()
            connection.close()
            context = make_context([first, second, settings, other])
            _, rows, source = zangichats.__wrapped__(context)
            self.assertEqual(len(rows), 12)
            self.assertEqual([row[11] for row in rows], [str(first)] * 6 + [str(second)] * 6)
            self.assertEqual(source, str(first) + '\n' + str(second))

    def test_joined_names_and_raw_direction_replace_local_user_derivations(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _ = make_database(pathlib.Path(directory) / 'messages.db')
            headers, rows, _ = zangichats.__wrapped__(make_context([path]))
            self.assertEqual(headers[1:4], ('isIncoming (as stored)', 'From Name (joined)', 'Chat'))
            self.assertEqual(rows[0][1:3], (0, 'Sender'))
            self.assertEqual((rows[0][9], rows[4][1], rows[4][2], rows[4][9]),
                             ('Receiver', 1, 'Sender', 'Receiver'))
            self.assertEqual(rows[1][1:3], (1, None))
            self.assertEqual(rows[2][1:3], (0, None))


    def test_null_text_numeric_incoming_and_duplicate_joined_profiles(self):
        with tempfile.TemporaryDirectory() as directory:
            path = make_raw_database(pathlib.Path(directory) / 'messages.db')
            headers, rows, _ = zangichats.__wrapped__(make_context([path]))
            self.assertEqual(len(rows), 19)
            self.assertEqual(len(headers), 12)
            expected = {6: None, 7: 'Outgoing', 8: '0', 9: 2, 10: 1.0}
            for message_id, incoming in expected.items():
                matching = [row for row in rows if row[7] == message_id]
                self.assertEqual(len(matching), 2)
                self.assertEqual({row[2] for row in matching}, {'Sender', 'DuplicateSender'})
                self.assertTrue(all(row[9] == 'Receiver' for row in matching))
                self.assertTrue(all(row[1] == incoming and type(row[1]) is type(incoming) for row in matching))
                self.assertTrue(all(row[8] == 20 and row[10] == 30 for row in matching))
            self.assertNotIn('From Me', headers)
            self.assertFalse(any('Local User' in row for row in rows))
            from scripts.artifacts.ZangiChats import __artifacts_v2__  # pylint: disable=import-outside-toplevel
            self.assertNotIn('data_views', __artifacts_v2__['zangichats'])


def make_raw_database(path):
    path, _ = make_database(path)
    connection = sqlite3.connect(path)
    connection.execute("INSERT INTO user_profile VALUES(20,'DuplicateSender',NULL)")
    records = [(1700000010000 + index * 1000, None if index % 2 else '',
                6 + index, 'raw' + str(index), 'raw incoming', None, 20, 30, incoming)
               for index, incoming in enumerate([None, 'Outgoing', '0', 2, 1.0])]
    connection.executemany('INSERT INTO message VALUES(?,?,?,?,?,?,?,?,?)', records)
    connection.commit()
    connection.close()
    return path


if __name__ == '__main__':
    unittest.main()
