"""Dropbox candidate rows retain their selected printable text evidence."""
import base64
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts.dropbox import dropbox_account  # pylint: disable=wrong-import-position
from scripts.ilapfuncs import convert_unix_ts_to_utc  # pylint: disable=wrong-import-position

RAW_HEADER = 'Raw Matched Candidate Text (JSON)'
CANDIDATE_LABELS = {'Email': 'Email-shaped Text Candidate',
                    'Dropbox ID': 'dbid:-prefixed Text Candidate',
                    'Plan': 'Dropbox-prefixed Text Candidate'}


def encoded_fields(strings):
    """Actual length-delimited wire fields, without asserting Dropbox field meanings."""
    raw = b''
    for text in strings:
        value = text.encode('ascii')
        assert len(value) < 32
        raw += b'\x0a' + bytes([len(value)]) + value
    return base64.b64encode(raw).decode('ascii')


def make_database(root, name='one-prefs.db'):
    path = Path(root) / 'data/user/0/com.dropbox.android/databases' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE DropboxAccountPrefs(pref_name,pref_value)')
    rows = [
        ('ACCOUNT_INFO', encoded_fields(['old@example.org'])),
        ('ACCOUNT_INFO', encoded_fields(['a@example.org', 'b@example.org', 'dbid:ABC',
                                        'dbid:DEF', ' *(Dropbox Plus)* ', 'Dropbox Plus',
                                        'Dropbox Plus', 'Dropbox Pro', 'xDropbox No'])),
        ('FULL_ACCOUNT_INFO_V2', encoded_fields(['a@example.org', 'dbid:ABC',
                                               '"Dropbox Plus"', 'Dropbox Pro'])),
        ('PLAN_INFO_V2', encoded_fields(['(Dropbox Plus)', 'Dropbox Pro'])),
        ('PHOTO_UPLOAD_LAST_DESTINATION', 'folder'), ('LAST_URI', 'content://item'),
        ('IS_SIGN_UP', '0'), ('UPGRADE_SOURCE_FOR_JTBD', ''),
        ('USER_SIGN_UP_DATE', '1700000000123'), ('LAST_USER_LOGIN_TIME', 'invalid'),
        ('NOTIFICATION_PERMISSION_REQUEST_TIMESTAMP', '0'),
        ('LAST_TIME_OVER_QUOTA_WARNING_PAGE_SHOWN', None),
    ]
    con.executemany('INSERT INTO DropboxAccountPrefs VALUES(?,?)', rows)
    con.commit()
    assert con.execute('PRAGMA quick_check').fetchone()[0] == 'ok'
    con.close()
    return path


def parse(path):
    return dropbox_account.__wrapped__(SimpleNamespace(get_files_found=lambda: [str(path)]))


class DropboxCandidateTextTest(unittest.TestCase):
    def test_actual_wire_matches_aggregation_repeats_and_direct_preferences(self):
        with tempfile.TemporaryDirectory() as root:
            path = make_database(root)
            headers, rows, source = parse(path)
            self.assertEqual(headers, ('Property / Candidate', 'Value / Derived Display',
                                       RAW_HEADER, 'Source Preference'))
            self.assertEqual(source, str(path))
            self.assertEqual(len(rows), 10)
            self.assertEqual([r[0] for r in rows[:4]],
                             [CANDIDATE_LABELS['Email'], CANDIDATE_LABELS['Dropbox ID'],
                              CANDIDATE_LABELS['Plan'], CANDIDATE_LABELS['Plan']])
            self.assertEqual([r[1] for r in rows[:4]],
                             ['a@example.org', 'dbid:ABC', 'Dropbox Plus', 'Dropbox Pro'])
            self.assertNotIn('old@example.org', str(rows))  # Existing last-row-wins behavior.
            self.assertNotIn('b@example.org', str(rows))  # Existing first regex match only.
            self.assertNotIn('dbid:DEF', str(rows))
            expected = [('ACCOUNT_INFO', ' *(Dropbox Plus)* '), ('ACCOUNT_INFO', 'Dropbox Plus'),
                        ('ACCOUNT_INFO', 'Dropbox Plus'), ('FULL_ACCOUNT_INFO_V2', '"Dropbox Plus"'),
                        ('PLAN_INFO_V2', '(Dropbox Plus)')]
            decoded = json.loads(rows[2][2])
            self.assertEqual(decoded, [dict(source_preference=p, matched_text=t) for p, t in expected])
            self.assertEqual(rows[2][2], json.dumps(decoded, ensure_ascii=False, separators=(',', ':')))
            self.assertEqual(rows[2][3], ', '.join(p for p, _ in expected))
            self.assertEqual(json.loads(rows[0][2]), [
                {'source_preference': p, 'matched_text': 'a@example.org'}
                for p in ['ACCOUNT_INFO', 'FULL_ACCOUNT_INFO_V2']])
            self.assertEqual([r[1] for r in rows[4:]],
                             ['folder', 'content://item', '0', convert_unix_ts_to_utc(1700000000123),
                              'invalid', 0])
            self.assertTrue(all(r[2] == '' for r in rows[4:]))

    def test_no_match_invalid_base64_and_first_main_selection(self):
        with tempfile.TemporaryDirectory() as root:
            first = make_database(root)
            other = make_database(root, 'two-prefs.db')
            con = sqlite3.connect(other)
            con.execute('DELETE FROM DropboxAccountPrefs')
            con.executemany('INSERT INTO DropboxAccountPrefs VALUES(?,?)', [
                ('ACCOUNT_INFO', 'a'), ('FULL_ACCOUNT_INFO_V2', '!!!'),
                ('PLAN_INFO_V2', encoded_fields(['xDropbox No', 'no candidate']))])
            con.commit()
            con.close()
            headers, rows, source = dropbox_account.__wrapped__(SimpleNamespace(
                get_files_found=lambda: [str(first) + '-wal', str(other), str(first)]))
            self.assertEqual(rows, [])
            self.assertEqual(source, str(other))
            self.assertNotIn('Source File', headers)
