"""CD0082: retain message records when the user lookup has no matching row.

The fixture defines only fields used by the existing query. It is not evidence of
an app schema: no registered real corpus holds the target database.
"""
import datetime
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.artifacts.WordsWithFriends import get_WordsWithFriends


class WordsWithFriendsUnmatchedUsers(unittest.TestCase):
    def parse(self, users, messages):
        with tempfile.TemporaryDirectory() as directory:
            source = pathlib.Path(directory) / 'wf_database.sqlite'
            con = sqlite3.connect(source)
            con.executescript('''
                CREATE TABLE users (zynga_account_id INTEGER, name TEXT, email_address TEXT);
                CREATE TABLE messages (created_at INTEGER, conv_id TEXT,
                    user_zynga_id INTEGER, text TEXT);
            ''')
            con.executemany('INSERT INTO users VALUES (?, ?, ?)', users)
            con.executemany('INSERT INTO messages VALUES (?, ?, ?, ?)', messages)
            con.commit()
            con.close()
            return get_WordsWithFriends.__wrapped__(SimpleNamespace(get_files_found=lambda: [source]))

    def test_matched_unmatched_null_and_repeated_records_survive(self):
        users = [(10, 'Player', 'player@example.com'), (20, '', None)]
        repeated = (2000, 'second', 99, 'unmatched')
        messages = [(1000, 'first', 10, 'matched'), repeated, repeated,
                    (3000, 'third', None, 'null identity'), (0, 'fourth', 20, 'empty name')]
        headers, rows, _ = self.parse(users, messages)
        self.assertEqual(len(rows), 5)
        self.assertEqual(headers[0], ('Chat Message Creation', 'datetime'))
        self.assertEqual(headers[-1], 'User Zynga ID')
        self.assertEqual(rows[0][1:], ('third', None, None, 'null identity', None))
        self.assertEqual(rows[1], rows[2])
        self.assertEqual(rows[1][1:], ('second', None, None, 'unmatched', 99))
        self.assertEqual(rows[3], (datetime.datetime(1970, 1, 1, 0, 0, 1,
                                                   tzinfo=datetime.timezone.utc),
                                   'first', 'Player', 'player@example.com', 'matched', 10))
        self.assertEqual(rows[4], ('', 'fourth', '', None, 'empty name', 20))

    def test_multiple_matching_user_rows_are_not_silently_deduplicated(self):
        _, rows, _ = self.parse([(10, 'First', None), (10, 'Second', None)],
                               [(1000, 'chat', 10, 'message')])
        self.assertEqual(len(rows), 2)
        self.assertEqual({row[2] for row in rows}, {'First', 'Second'})
        self.assertEqual({row[-1] for row in rows}, {10})


if __name__ == '__main__':
    unittest.main()
