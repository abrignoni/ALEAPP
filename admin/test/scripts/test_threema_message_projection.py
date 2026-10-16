"""Constructed SQL rows exercise file labels and existing message dates."""
import datetime
import json
import sqlite3
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from scripts.artifacts import Threema


class ThreemaMessageProjectionTest(unittest.TestCase):
    def project(self, records):
        connection = sqlite3.connect(':memory:')
        connection.execute('CREATE TABLE contacts(identity,firstName,lastName,publicNickName)')
        connection.execute("INSERT INTO contacts VALUES('CONTACT','First','Last','Nickname')")
        connection.execute('CREATE TABLE message(identity,outbox,type,body,apiMessageId,'
                           'quotedMessageId,state,isRead,createdAtUtc,deliveredAtUtc,readAtUtc)')
        connection.executemany('INSERT INTO message VALUES(?,?,?,?,?,?,?,?,?,?,?)', records)
        context = SimpleNamespace(get_files_found=lambda: [])
        with patch.object(Threema, '_decrypted_connections', return_value=[(connection, 'store')]):
            return Threema.threema_messages.__wrapped__(context)

    def test_files_keep_mime_and_metadata_with_adjacent_nullable_dates(self):
        mimes = ['image/jpeg', 'video/mp4', 'application/pdf', '']
        records = [('CONTACT', 1, 8, json.dumps(['file.bin', mime, 42]),
                    str(index), None, 'SENT', 0, 1700000000000 + index * 1000,
                    1700000060000 if index % 2 == 0 else None,
                    1700000120000 if index % 2 == 0 else None)
                   for index, mime in enumerate(mimes)]
        headers, rows, source = self.project(records)
        self.assertEqual(headers[:3], (('Created', 'datetime'), ('Delivered', 'datetime'),
                                       ('Read At', 'datetime')))
        self.assertNotIn('Source File', headers)
        self.assertEqual(source, 'store')
        self.assertEqual(len(rows), 4)
        for index, row in enumerate(rows):
            with self.subTest(mime=mimes[index]):
                self.assertEqual(row[3:9], ('First Last', 'Sent', 'File', 'file.bin', mimes[index], 42))
                self.assertEqual(row[0], datetime.datetime.fromtimestamp(1700000000 + index,
                                                                        datetime.timezone.utc))
                if index % 2 == 0:
                    self.assertEqual(row[1:3], (datetime.datetime.fromtimestamp(1700000060, datetime.timezone.utc),
                                               datetime.datetime.fromtimestamp(1700000120, datetime.timezone.utc)))
                else:
                    self.assertEqual(row[1:3], (None, None))

    def test_text_quotes_location_and_call_keep_stored_values(self):
        bodies = [(0, 'hello', 'original', None),
                  (0, 'reply', 'reply', 'original'),
                  (4, json.dumps([12.5, -45.5, 3, 'Address']), 'location', None),
                  (9, json.dumps([{'status': 'finished', 'callId': 'call', 'duration': 9}]), 'call', None)]
        records = [('CONTACT', 0, kind, body, api, quoted, 'RECEIVED', 1,
                    1700000000000 + index * 1000, None, None)
                   for index, (kind, body, api, quoted) in enumerate(bodies)]
        _, rows, _ = self.project(records)
        self.assertEqual([row[5] for row in rows], ['Text', 'Text', 'Location', 'Call'])
        self.assertEqual(rows[1][-1], 'hello')
        self.assertEqual(rows[2][9:12], (12.5, -45.5, 3))
        self.assertEqual(rows[2][6], 'Address')
        self.assertEqual(rows[3][12:15], ('finished', 'call', 9))
        self.assertTrue(all(row[4] == 'Received' and row[-2] == 'Yes' for row in rows))


if __name__ == '__main__':
    unittest.main()
