"""Provider databases rebuilt by ALEX: its default rows are left out, device databases are untouched.

ALEX declares every column TEXT, leaves user_version at 0 and, for a provider that returned
no rows, inserts one row made of its defaults with _id 0 and times 0 (ALEAPP #2076). All
values here are synthetic.
"""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.ilapfuncs import is_alex_rebuilt_provider_db, alex_default_row_filter  # pylint: disable=wrong-import-position
from scripts.artifacts.smsmms import get_sms_mms, get_sms_mms_mms, get_sms_mms_combined  # pylint: disable=wrong-import-position
from scripts.artifacts.calllog import get_calllog, get_calllog_phone_accounts  # pylint: disable=wrong-import-position
from scripts.artifacts.googleCalendar import get_calendar, get_calendar_calendars  # pylint: disable=wrong-import-position

SMS_COLS = ('_id', 'thread_id', 'address', 'person', 'date', 'date_sent', 'read', 'type', 'body',
            'service_center', 'error_code')
PDU_COLS = ('_id', 'thread_id', 'date', 'date_sent', 'read', 'msg_box')
PART_COLS = ('_id', 'mid', 'seq', 'ct', 'cl', '_data', 'text')
ADDR_COLS = ('_id', 'msg_id', 'address', 'type')
CALL_COLS = ('_id', 'date', 'phone_account_address', 'number', 'type', 'duration', 'geocoded_location',
             'countryiso', '_data', 'mime_type', 'transcription', 'deleted', 'subscription_id',
             'subscription_component_name')
EVENT_COLS = ('_id', 'calendar_id', 'dtstart', 'dtend', 'eventTimezone', 'title', 'description',
              'eventLocation', '_sync_id', 'organizer', 'allDay', 'hasAlarm')
CAL_COLS = ('_id', 'cal_sync8', 'name', 'calendar_displayName', 'account_name', 'account_type', 'visible',
            'calendar_location', 'calendar_timezone', 'ownerAccount', 'isPrimary', 'calendar_color',
            'calendar_color_index')

SMS_REAL = ('1', '1', '+15550100001', None, '1767225600000', '0', '1', '1', 'Synthetic body', None, '-1')
SMS_DEFAULT = ('0', '0', None, '0', '0', '0', '0', '0', None, None, '-1')
CALL_REAL = ('1', '1767225600000', None, '+15550100002', '1', '74', None, 'US', None, None, None, '0', '1', None)
CALL_DEFAULT = ('0', '0', None, None, '0', '0', None, None, None, None, None, '0', '-1', None)
EVENT_REAL = ('1', '1', '1767265200000', '1767268800000', 'UTC', 'Synthetic event', None, None, None, None, '0', '0')
EVENT_DEFAULT = ('0', '0', '0', None, None, None, None, None, None, None, '0', '0')
CAL_REAL = ('1', None, 'Synthetic', 'Synthetic', 'test@example.com', 'LOCAL', '1', None, 'UTC', None, '1', None, None)
CAL_DEFAULT = ('0', None, None, None, None, None, '1', None, None, None, None, None, None)


def make_db(path, tables, rebuilt):
    """tables: {name: (columns, rows)}. rebuilt mimics ALEX (TEXT columns, user_version 0);
    otherwise a device-style schema with _id INTEGER and a non-zero user_version."""
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    for name, (columns, rows) in tables.items():
        if rebuilt:
            col_def = ', '.join(f'"{c}" TEXT' for c in columns)
        else:
            col_def = ', '.join('_id INTEGER PRIMARY KEY' if c == '_id' else c for c in columns)
        con.execute(f'CREATE TABLE "{name}" ({col_def})')
        con.executemany(f'INSERT INTO "{name}" VALUES ({",".join("?" * len(columns))})', rows)
    if not rebuilt:
        con.execute('PRAGMA user_version = 12')
    con.commit()
    con.close()


def run(root, paths, artifact):
    context = SimpleNamespace(get_files_found=lambda: list(map(str, paths)),
                              get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))
    return artifact.__wrapped__(context)


def mmssms_tables(sms_rows, pdu_rows):
    return {'sms': (SMS_COLS, sms_rows), 'pdu': (PDU_COLS, pdu_rows), 'part': (PART_COLS, []),
            'addr': (ADDR_COLS, [])}


class AlexRebuiltDetectionTest(unittest.TestCase):
    def test_marker(self):
        with tempfile.TemporaryDirectory() as root:
            base = pathlib.Path(root)
            rebuilt = base / 'rebuilt.db'
            device = base / 'device.db'
            stub = base / 'stub.db'
            integer_v0 = base / 'integer_v0.db'
            make_db(rebuilt, {'calls': (CALL_COLS, [CALL_REAL])}, rebuilt=True)
            make_db(device, {'calls': (CALL_COLS, [CALL_REAL])}, rebuilt=False)
            make_db(stub, {'logs': (('_id', 'date'), [])}, rebuilt=True)  # no main table
            con = sqlite3.connect(integer_v0)
            con.execute('CREATE TABLE calls (_id INTEGER PRIMARY KEY, date INTEGER)')
            con.commit()
            con.close()
            self.assertTrue(is_alex_rebuilt_provider_db(str(rebuilt)))
            self.assertFalse(is_alex_rebuilt_provider_db(str(device)))
            self.assertFalse(is_alex_rebuilt_provider_db(str(stub)))
            self.assertFalse(is_alex_rebuilt_provider_db(str(integer_v0)))
            self.assertEqual(alex_default_row_filter(str(device), 'calls'), '1')
            self.assertEqual(alex_default_row_filter(str(rebuilt), 'calls', 'c'),
                             '("c"._id IS NULL OR "c"._id != \'0\')')


class AlexRebuiltArtifactsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.root = pathlib.Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _mmssms(self, rebuilt, sms_rows, pdu_rows):
        path = self.root / 'data/data/com.android.providers.telephony/databases/mmssms.db'
        make_db(path, mmssms_tables(sms_rows, pdu_rows), rebuilt)
        return path

    def test_sms_default_row_left_out_and_text_zero_is_no_date(self):
        path = self._mmssms(True, [SMS_DEFAULT, SMS_REAL], [('0', '0', '0', '0', '0', '0')])
        _, rows, _ = run(self.root, [path], get_sms_mms)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][4], 'Synthetic body')
        self.assertEqual(rows[0][0].year, 2026)
        self.assertEqual(rows[0][1], '')  # date_sent stored as '0'
        _, mms_rows, _ = run(self.root, [path], get_sms_mms_mms)
        self.assertEqual(mms_rows, [])
        _, combined, _ = run(self.root, [path], get_sms_mms_combined)
        self.assertEqual(len(combined), 1)

    def test_mms_direction_from_text_msg_box(self):
        pdu_real = ('1', '1', '1767225600', '0', '1', '2')
        pdu_null_id = (None, '1', '1767225600', '0', '1', '1')
        path = self._mmssms(True, [], [('0', '0', '0', '0', '0', '0'), pdu_real, pdu_null_id])
        _, rows, _ = run(self.root, [path], get_sms_mms_mms)
        self.assertEqual(sorted(r[2] for r in rows), ['Received', 'Sent'])

    def test_device_database_untouched(self):
        device_default = (0,) + SMS_DEFAULT[1:]
        path = self._mmssms(False, [device_default, SMS_REAL], [])
        _, rows, _ = run(self.root, [path], get_sms_mms)
        self.assertEqual(len(rows), 2)

    def test_calllog(self):
        path = self.root / 'data/data/com.android.providers.contacts/databases/calllog.db'
        make_db(path, {'calls': (CALL_COLS, [CALL_DEFAULT, CALL_REAL])}, rebuilt=True)
        _, rows, _ = run(self.root, [path], get_calllog)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][4], '+15550100002')
        _, accounts, _ = run(self.root, [path], get_calllog_phone_accounts)
        self.assertEqual([a[-1] for a in accounts], [1])
        self.assertEqual(accounts[0][0].year, 2026)

    def test_calendar(self):
        path = self.root / 'data/data/com.android.providers.calendar/databases/calendar.db'
        make_db(path, {'Events': (EVENT_COLS, [EVENT_DEFAULT, EVENT_REAL]),
                       'Calendars': (CAL_COLS, [CAL_DEFAULT, CAL_REAL])}, rebuilt=True)
        _, events, _ = run(self.root, [path], get_calendar)
        self.assertEqual([e[3] for e in events], ['Synthetic event'])
        _, calendars, _ = run(self.root, [path], get_calendar_calendars)
        self.assertEqual([c[1] for c in calendars], ['Synthetic'])
        self.assertEqual(calendars[0][0], '')  # cal_sync8 empty


if __name__ == '__main__':
    unittest.main()
