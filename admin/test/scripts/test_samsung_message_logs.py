"""Samsung calls-table message rows go to Samsung Message Logs, not to Call logs."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts.calllog import get_calllog  # pylint: disable=wrong-import-position
from scripts.artifacts.samsungMessageLogs import get_samsung_message_logs  # pylint: disable=wrong-import-position

SMS_DATE = 1700000000000
MMS_DATE = 1700000100000


def make_calllog(root, user_dir, package='com.samsung.android.providers.contacts'):
    path = pathlib.Path(root) / user_dir / package / 'databases/calllog.db'
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE calls(_id INTEGER PRIMARY KEY, date, last_modified, number, name, type, duration, '
                'phone_account_address, geocoded_location, countryiso, _data, mime_type, transcription, deleted, '
                'logtype, messageid TEXT, sec_msg_id, m_subject, m_content)')
    rows = [
        (1, SMS_DATE - 5000, SMS_DATE - 5000, '100', None, 2, 20, None, None, 'US', None, None, None, 0, 1000, None, None, None, None),
        (2, SMS_DATE - 9000, SMS_DATE - 9000, '100', None, 3, 0, None, None, 'US', None, None, None, 0, 100, None, None, None, None),
        (3, SMS_DATE, SMS_DATE, '100', 'KD', 2, 0, None, None, 'US', None, None, None, 0, 300, '7', 'a1', None, 'text one'),
        (4, SMS_DATE + 1, SMS_DATE + 1, '100', 'KD', 1, 0, None, None, 'US', None, None, None, 0, 300, '8', 'a2', None, 'text two'),
        (5, MMS_DATE, MMS_DATE, '100', 'KD', 2, 0, None, None, 'US', None, None, None, 0, 200, '3', 'a3', None, None),
    ]
    con.executemany(f'INSERT INTO calls VALUES({",".join("?" * 19)})', rows)
    con.commit()
    con.close()
    return path


def make_mmssms(root, user_dir):
    path = pathlib.Path(root) / user_dir / 'com.android.providers.telephony/databases/mmssms.db'
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE sms(_id INTEGER PRIMARY KEY, date, type)')
    con.execute('CREATE TABLE pdu(_id INTEGER PRIMARY KEY, date, msg_box)')
    # id 7 matches on id and date; id 8 exists with another date, so it is not a match
    con.executemany('INSERT INTO sms VALUES(?,?,?)', [(7, SMS_DATE, 2), (8, SMS_DATE - 60000, 1)])
    con.execute('INSERT INTO pdu VALUES(?,?,?)', (3, MMS_DATE // 1000, 2))
    con.commit()
    con.close()
    return path


def context_for(root, paths):
    return SimpleNamespace(get_files_found=lambda: [str(p) for p in paths],
                           get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))


class SamsungMessageLogsTest(unittest.TestCase):
    def test_split_and_provider_states(self):
        with tempfile.TemporaryDirectory() as root:
            user0 = make_calllog(root, 'data/data')
            user10 = make_calllog(root, 'data/user/10')
            provider = make_mmssms(root, 'data/data')
            context = context_for(root, [user0, user10, provider])

            _headers, calls, _source = get_calllog.__wrapped__(context)
            self.assertEqual(len(calls), 4)  # 1000 and 100 rows of both users

            headers, rows, source = get_samsung_message_logs.__wrapped__(context)
            self.assertEqual(len(rows), 6)
            self.assertIn(str(provider), source.split('\n'))
            col = {name if isinstance(name, str) else name[0]: i for i, name in enumerate(headers)}
            states = sorted((r[col['Log ID']], r[col['Message Type']], r[col['Direction']],
                             r[col['Telephony Provider Row']]) for r in rows)
            self.assertEqual(states, [
                (3, 'SMS', 'Sent', 'Matched (same id and date)'),
                (3, 'SMS', 'Sent', 'Not checked (no readable mmssms.db for this Android user)'),
                (4, 'SMS', 'Received', 'No provider row with this id and date'),
                (4, 'SMS', 'Received', 'Not checked (no readable mmssms.db for this Android user)'),
                (5, 'MMS', 'Sent', 'Matched (same id and date)'),
                (5, 'MMS', 'Sent', 'Not checked (no readable mmssms.db for this Android user)'),
            ])

    def test_filter_applies_only_to_the_samsung_provider(self):
        with tempfile.TemporaryDirectory() as root:
            path = make_calllog(root, 'data/data', package='com.android.providers.contacts')
            _headers, calls, _source = get_calllog.__wrapped__(context_for(root, [path]))
            self.assertEqual(len(calls), 5)

    def test_table_without_logtype_is_not_read(self):
        with tempfile.TemporaryDirectory() as root:
            path = pathlib.Path(root) / 'data/data/com.samsung.android.providers.contacts/databases/calllog.db'
            path.parent.mkdir(parents=True)
            con = sqlite3.connect(path)
            con.execute('CREATE TABLE calls(_id INTEGER PRIMARY KEY, date, type, number)')
            con.execute('INSERT INTO calls VALUES(1, 1, 2, "1")')
            con.commit()
            con.close()
            _headers, rows, _source = get_samsung_message_logs.__wrapped__(context_for(root, [path]))
            self.assertEqual(rows, [])


if __name__ == '__main__':
    unittest.main()
