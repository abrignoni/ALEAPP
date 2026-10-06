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
            context = SimpleNamespace(get_files_found=lambda: [str(path)])
            with patch('scripts.artifacts.ZangiChats.check_in_media') as media:
                headers, rows, source = zangichats.__wrapped__(context)
            self.assertEqual(len(headers), 11)
            self.assertEqual(headers[0], ('Timestamp', 'datetime'))
            self.assertNotIn('Source File', headers)
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

    def test_existing_name_and_direction_derivations_are_unchanged_not_validated(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _ = make_database(pathlib.Path(directory) / 'messages.db')
            headers, rows, _ = zangichats.__wrapped__(SimpleNamespace(get_files_found=lambda: [str(path)]))
            self.assertEqual(headers[1:4], ('From Me', 'Sender Name', 'Chat'))
            self.assertEqual(rows[0][1:3], (1, 'Local User'))
            self.assertEqual((rows[0][9], rows[4][1], rows[4][2], rows[4][9]),
                             ('Receiver', 0, 'Sender', 'Local User'))
            self.assertEqual(rows[1][1:3], (0, None))
            self.assertEqual(rows[2][1:3], (1, 'Local User'))


if __name__ == '__main__':
    unittest.main()
