"""Selected legacy admin records retain raw values and malformed JSON evidence."""
from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from admin.test.scripts.test_messenger_evidence_scope import run
from scripts.artifacts import FacebookMessenger as messenger


def create_admin_fixture(root, malformed=True):
    root = Path(root)
    sender = json.dumps({'name': 'sender <name>', 'user_key': 'FACEBOOK:77'})
    cases = [('false', {'video': False, 'call_duration': 5, 'caller_id': 999}, sender, 1700000000000),
             ('true', {'video': True, 'call_duration': 90061}, sender, 1700000001000),
             ('missing', {}, sender, 1700000002000),
             ('null', {'video': None, 'call_duration': None}, sender, None),
             ('zero', {'video': 0, 'call_duration': 0}, sender, 0),
             ('one', {'video': 1, 'call_duration': 1}, sender, 1700000003000),
             ('unknown', {'video': 2, 'call_duration': -1}, sender, 1700000004000),
             ('text', {'video': 'unknown', 'call_duration': 'unknown'}, sender, None),
             ('array', ['not', 'a', 'call'], sender, 1700000005000),
             ('no-sender', {'video': False, 'call_duration': 5}, None, 1700000006000)]
    cases.append(cases[0])
    if malformed:
        cases.extend([('bad-meta', '{invalid <json>', sender, 1700000007000),
                      ('empty-meta', '', sender, 1700000008000),
                      ('bad-sender', {'video': True, 'call_duration': 5}, '{invalid <sender>',
                       1700000009000)])
    files = []
    for user in [0, 10]:
        path = root/f'A/data/user/{user}/com.facebook.orca/databases/threads_db2'
        path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(path)
        db.executescript('CREATE TABLE threads(thread_key); INSERT INTO threads VALUES("thread");'
                         'CREATE TABLE messages(timestamp_ms,sender,thread_key,msg_id,'
                         'generic_admin_message_extensible_data);')
        for ident, meta, raw_sender, timestamp in cases if user == 0 else cases[:1]:
            raw_meta = meta if isinstance(meta, str) else json.dumps(meta, ensure_ascii=False)
            db.execute('INSERT INTO messages VALUES(?,?,?,?,?)',
                       (timestamp, raw_sender, 'thread', ident, raw_meta))
        db.execute('INSERT INTO messages VALUES(?,?,?,?,?)',
                   (1700000000000, sender, 'thread', 'excluded-null', None))
        db.execute('INSERT INTO messages VALUES(?,?,?,?,?)',
                   (1700000000000, sender, 'unmatched', 'excluded-thread', '{}'))
        db.commit()
        db.close()
        files.append(path)
    return files


class TestMessengerAdminMetadata(unittest.TestCase):
    def test_raw_values_malformed_rows_and_source_multiplicity(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_admin_fixture(directory)
            with patch.object(messenger, 'logfunc') as logs:
                headers, raw_rows = run(directory, files, 'get_fb_threads_calls')
            rows = [dict(zip(headers, row)) for row in raw_rows]
            self.assertEqual(len(rows), 15)
            self.assertEqual(headers[:3], ['Message Timestamp', 'Derived Timestamp',
                                          'Message Timestamp MS (as stored)'])
            self.assertEqual(sum(r['Message ID'] == 'false' for r in rows), 3)
            self.assertTrue(all(not r['Message ID'].startswith('excluded') for r in rows))
            values = {r['Message ID']: r for r in rows}
            self.assertEqual([values[k]['Video (as stored)'] for k in
                              ['false', 'true', 'missing', 'null', 'zero', 'one', 'unknown', 'text']],
                             [0, 1, None, None, 0, 1, 2, 'unknown'])
            self.assertEqual(values['true']['Duration HH:MM:SS'], '01:01:01')
            self.assertEqual(values['true']['Call Duration (as stored)'], 90061)
            self.assertEqual(values['false']['Metadata Caller ID'], 999)
            self.assertEqual(values['false']['Sender ID'], '77')
            self.assertEqual(values['false']['Derived Timestamp'].timestamp(), 1699999995)
            self.assertEqual(values['zero']['Message Timestamp'].timestamp(), 0)
            self.assertEqual(values['null']['Message Timestamp'], '')
            self.assertIsNone(values['null']['Message Timestamp MS (as stored)'])
            for ident in ['bad-meta', 'empty-meta']:
                self.assertIsNone(values[ident]['Video (as stored)'])
                self.assertEqual(values[ident]['Derived Timestamp'], '')
            self.assertEqual(values['bad-meta']['Admin Metadata (as stored)'], '{invalid <json>')
            self.assertEqual(values['empty-meta']['Admin Metadata (as stored)'], '')
            self.assertIsNone(values['bad-sender']['Sender Name'])
            self.assertEqual(values['bad-sender']['Sender JSON (as stored)'], '{invalid <sender>')
            self.assertTrue(any('preserved 2 rows with invalid metadata JSON and 1 rows' in str(c)
                                for c in logs.call_args_list))
            for source in files:
                db = sqlite3.connect(source)
                expected = db.execute('SELECT msg_id,generic_admin_message_extensible_data,sender '
                                      'FROM messages WHERE thread_key="thread" AND '
                                      'generic_admin_message_extensible_data IS NOT NULL').fetchall()
                db.close()
                actual = [(r['Message ID'], r['Admin Metadata (as stored)'], r['Sender JSON (as stored)'])
                          for r in rows if r['Source File'] == str(source.relative_to(directory))]
                self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
