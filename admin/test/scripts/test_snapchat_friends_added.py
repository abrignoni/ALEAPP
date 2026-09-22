"""get_snapchat_friends must report only the Friend rows whose addedTimestamp is above 0.

main.db's Friend table is not a friends list. On the tested images most of its rows carried
no addedTimestamp at all, and some carried 0: the account's own row, the teamsnapchat and
snapchatai accounts, and users whose reverseAddedTimestamp was set. The artifact used to
select addedTimestamp IS NOT NULL, which admitted every 0 row with an empty Added Timestamp.

These tests build synthetic stores (no real evidence bytes) holding one row of each kind and
assert that only the two rows with an addedTimestamp above 0 come back, with both timestamps
converted and the link type as stored. The second runs an older schema that lacks the
reverseAddedTimestamp and friendLinkType columns, which must still report its rows with
those two columns blank. Both fail on the pre-fix code, which returns the three 0 rows as
well.
"""
import datetime
import os
import sqlite3
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, REPO_ROOT)

from scripts.context import Context  # noqa: E402  pylint: disable=wrong-import-position
from scripts.artifacts.snapchat import (  # noqa: E402  pylint: disable=wrong-import-position
    get_snapchat_friends)

_FRIENDS = get_snapchat_friends.__wrapped__
_UTC = datetime.timezone.utc


def _ms(*args):
    """Milliseconds since the epoch for a UTC date, built from the date rather than by hand."""
    moment = datetime.datetime(*args, tzinfo=_UTC)
    return int(moment.timestamp()) * 1000 + moment.microsecond // 1000


# Awkward millisecond fractions, so a conversion that drops them cannot pass.
MUTUAL_ADDED = _ms(2023, 3, 4, 5, 6, 7, 123000)
MUTUAL_REVERSE = _ms(2023, 3, 5, 8, 9, 10, 456000)
OUTGOING_ADDED = _ms(2024, 11, 30, 23, 59, 58, 789000)
ONE_WAY_REVERSE = _ms(2022, 7, 1, 12, 0, 0, 1000)

# (userId, username, displayName, addedTimestamp, reverseAddedTimestamp, friendLinkType)
ROWS = [
    ('00000000-0000-4000-8000-000000000001', 'account_self', 'Self', 0, 0, 0),
    ('00000000-0000-4000-8000-000000000002', 'teamsnapchat', 'Team Snapchat', 0, 0, 0),
    ('00000000-0000-4000-8000-000000000003', 'added_me_only', 'Added Me', 0, ONE_WAY_REVERSE, 6),
    ('00000000-0000-4000-8000-000000000004', 'suggested_user', 'Suggested', None, None, None),
    ('00000000-0000-4000-8000-000000000005', 'mutual_user', 'Mutual', MUTUAL_ADDED, MUTUAL_REVERSE, 0),
    ('00000000-0000-4000-8000-000000000006', 'outgoing_user', 'Outgoing', OUTGOING_ADDED, 0, 1),
]


class SnapchatFriendsAddedTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_folder = os.path.join(self.tmp.name, 'report', 'data')
        Context.set_data_folder(self.data_folder)
        self.db_path = os.path.join(
            self.data_folder, 'Dump/data/data/com.snapchat.android/databases/main.db')
        os.makedirs(os.path.dirname(self.db_path))

    def tearDown(self):
        Context.clear()
        self.tmp.cleanup()

    def _build(self, current_schema=True):
        extra = ', reverseAddedTimestamp INTEGER, friendLinkType INTEGER' if current_schema else ''
        con = sqlite3.connect(self.db_path)
        con.execute('CREATE TABLE Friend(_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, '
                    'userId TEXT NOT NULL UNIQUE, displayName TEXT, phone TEXT, birthday INTEGER, '
                    f'addedTimestamp INTEGER{extra})')
        for user_id, username, display, added, reverse, link in ROWS:
            if current_schema:
                con.execute('INSERT INTO Friend(userId, username, displayName, addedTimestamp, '
                            'reverseAddedTimestamp, friendLinkType) VALUES (?, ?, ?, ?, ?, ?)',
                            (user_id, username, display, added, reverse, link))
            else:
                con.execute('INSERT INTO Friend(userId, username, displayName, addedTimestamp) '
                            'VALUES (?, ?, ?, ?)', (user_id, username, display, added))
        con.commit()
        con.close()

    def _run(self):
        Context.set_files_found([self.db_path])
        return _FRIENDS(Context)

    def test_only_rows_the_account_added_are_reported(self):
        self._build()
        headers, rows, source_path = self._run()

        # The own row, teamsnapchat and the user who only added the account hold 0, and the
        # suggested user holds NULL; none of them was added by the account. The pre-fix
        # IS NOT NULL query returned the three 0 rows as well, 5 rows in all.
        self.assertEqual(len(rows), 2, 'only the rows with an addedTimestamp above 0')
        self.assertEqual(headers, (('Added Timestamp', 'datetime'), ('Reverse Added Timestamp', 'datetime'),
                                   'Username', 'User ID', 'Display Name', 'Phone Nr', 'Birthday',
                                   'Friend Link Type (as stored)'))
        by_name = {row[2]: row for row in rows}
        self.assertEqual(sorted(by_name), ['mutual_user', 'outgoing_user'])

        mutual = by_name['mutual_user']
        self.assertEqual(mutual[0], datetime.datetime(2023, 3, 4, 5, 6, 7, 123000, tzinfo=_UTC))
        self.assertEqual(mutual[1], datetime.datetime(2023, 3, 5, 8, 9, 10, 456000, tzinfo=_UTC))
        self.assertEqual(mutual[3], '00000000-0000-4000-8000-000000000005')
        self.assertEqual(mutual[7], 0)

        outgoing = by_name['outgoing_user']
        self.assertEqual(outgoing[0], datetime.datetime(2024, 11, 30, 23, 59, 58, 789000, tzinfo=_UTC))
        self.assertEqual(outgoing[1], '', 'a reverseAddedTimestamp of 0 is reported blank')
        self.assertEqual(outgoing[7], 1)

        self.assertEqual(source_path, self.db_path)

    def test_older_schema_without_the_reverse_and_link_columns(self):
        self._build(current_schema=False)
        _headers, rows, _source_path = self._run()
        self.assertEqual(len(rows), 2, 'only the rows with an addedTimestamp above 0')
        by_name = {row[2]: row for row in rows}
        self.assertEqual(sorted(by_name), ['mutual_user', 'outgoing_user'])
        for row in rows:
            self.assertEqual(row[1], '', 'no reverseAddedTimestamp column, so the cell is blank')
            self.assertIsNone(row[7], 'no friendLinkType column, so the cell is empty')
        self.assertEqual(by_name['mutual_user'][0],
                         datetime.datetime(2023, 3, 4, 5, 6, 7, 123000, tzinfo=_UTC))


if __name__ == '__main__':
    unittest.main()
