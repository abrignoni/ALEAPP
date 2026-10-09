"""Use actual preference cursors to exercise both repeated scans and message matching."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.artifacts import thunderbird
from scripts.artifacts.thunderbird import _map_uuid_to_account
from scripts.ilapfuncs import get_sqlite_db_records


class TestThunderbirdCursorSnapshots(unittest.TestCase):
    uuids = ['11111111-1111-1111-1111-111111111111',
             '22222222-2222-2222-2222-222222222222']

    def preferences(self, root):
        path = root / 'preferences_storage'
        db = sqlite3.connect(path)
        db.execute('CREATE TABLE preferences_storage(primkey, value)')
        for index, uuid in enumerate(self.uuids):
            db.executemany('INSERT INTO preferences_storage VALUES(?,?)', [
                (uuid + '.email.0', str(index) + '@example.test'),
                (uuid + '.description', 'description-' + str(index)),
                (uuid + '.incomingServerSettings', json.dumps({
                    'username': str(index), 'password': 'p', 'host': 'host'}))])
        db.execute('INSERT INTO preferences_storage VALUES(?,?)',
                   (self.uuids[0] + '.outgoingServerSettings', '{"host":"out"}'))
        db.commit()
        db.close()
        return path

    def test_mapper_reuses_actual_one_pass_cursor(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.preferences(Path(temp))
            cursor = get_sqlite_db_records(str(path), 'SELECT * FROM preferences_storage')
            self.assertNotIsInstance(cursor, list)
            self.assertTrue(list(cursor))
            self.assertEqual(list(cursor), [])
            self.assertEqual(_map_uuid_to_account(str(path)),
                             dict(zip(self.uuids, ['0@example.test', '1@example.test'])))

    def test_each_account_sees_properties_and_missing_defaults(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.preferences(Path(temp))
            context = SimpleNamespace(get_files_found=lambda: [str(path)])
            _, rows, source = thunderbird.thunderbird_accounts.__wrapped__(context)
            by_address = {row[2]: row for row in rows}
            self.assertEqual(len(rows), 2)
            self.assertEqual(by_address['0@example.test'],
                             ('', 'description-0', '0@example.test', '', '0', 'p', 'host', 'out'))
            self.assertEqual(by_address['1@example.test'],
                             ('', 'description-1', '1@example.test', '', '1', 'p', 'host', ''))
            self.assertEqual(source, str(path))

    def test_mapped_message_join_multiplicity_and_unknown_uuid_skip(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pref = self.preferences(root)
            message = root / (self.uuids[1] + '.db')
            db = sqlite3.connect(message)
            db.execute('CREATE TABLE messages(id,date,internal_date,sender_list,to_list,'
                       'cc_list,bcc_list,subject,preview,attachment_count,read,flagged,'
                       'answered,forwarded,folder_id,empty)')
            db.execute('CREATE TABLE folders(id,name)')
            db.execute('CREATE TABLE messages_fulltext_content(docid,c0fulltext)')
            db.execute('INSERT INTO messages VALUES(1,NULL,NULL,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                       ('a,b', 'to', '', '', 'subject', 'preview', 0, 0, 0, 0, 0, 1, None))
            db.executemany('INSERT INTO folders VALUES(?,?)', [(1, 'one'), (1, 'two')])
            db.execute('INSERT INTO messages_fulltext_content VALUES(1,?)', ('<x>\nbody',))
            db.commit()
            db.close()
            unknown = root / '99999999-9999-9999-9999-999999999999.db'
            unknown.write_bytes(message.read_bytes())
            context = SimpleNamespace(get_files_found=lambda: [str(pref), str(message), str(unknown)])
            with patch.object(thunderbird.Context, 'get_relative_path',
                              side_effect=lambda p: str(Path(p).relative_to(root))):
                headers, rows, _ = thunderbird.thunderbird_messages.__wrapped__(context)
            self.assertEqual(len(headers), 17)
            self.assertEqual(len(rows), 2)
            self.assertEqual({row[15] for row in rows}, {'one', 'two'})
            for row in rows:
                self.assertEqual(row[0:4], (None, None, '1@example.test', 'a\nb'))
                self.assertEqual(row[9], '&lt;x&gt;<br>body')
                self.assertEqual(row[16], message.name)


if __name__ == '__main__':
    unittest.main()
