"""A settings or policy file that does not read cleanly does not lose what can still be read."""
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import notificationHistory as nh

TARGET = '<setting id="9" name="notification_history_enabled" value="1" package="android" />'
OTHER = '<setting id="1" name="other" value="plain" package="android" />'
BAD = '<setting id="2" name="broken" value="{"a":1}" package="android" />'


def status_rows(text, user='0'):
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / 'users' / user / 'settings_secure.xml'
        path.parent.mkdir(parents=True)
        path.write_text(text)
        context = SimpleNamespace(get_files_found=lambda: [str(path)])
        with patch.object(nh, 'logfunc') as log:
            _headers, rows, _source = nh.get_notificationHistory_status.__wrapped__(context)
    return rows, [call.args[0] for call in log.call_args_list]


class StatusFromDamagedXml(unittest.TestCase):
    def test_clean_file(self):
        rows, log = status_rows(f'<?xml version="1.0"?><settings version="1">{TARGET}</settings>')
        self.assertEqual(rows, [('Enabled', '0')])
        self.assertEqual(log, [])

    def test_second_root_element(self):
        rows, log = status_rows(f'<?xml version="1.0"?><settings version="1">{TARGET}</settings>\n<namespaceHashes></namespaceHashes>')
        self.assertEqual(rows, [('Enabled', '0')])
        self.assertTrue(any('settings_secure.xml' in line for line in log))

    def test_unescaped_quote_in_another_setting(self):
        rows, log = status_rows(f'<?xml version="1.0"?><settings version="1">{OTHER}{BAD}{TARGET}</settings>')
        self.assertEqual(rows, [('Enabled', '0')])
        self.assertTrue(any('1 could not be read' in line for line in log))

    def test_damaged_file_without_the_setting_gives_no_row(self):
        rows, _log = status_rows(f'<?xml version="1.0"?><settings version="1">{OTHER}{BAD}</settings>')
        self.assertEqual(rows, [])


class WhatTheFallbackReads(unittest.TestCase):
    DAMAGED = f'<?xml version="1.0"?><settings version="1">{OTHER}{BAD}'

    def test_a_setting_after_the_closing_tag_is_not_read(self):
        late = TARGET.replace('value="1"', 'value="0"')
        rows, _log = status_rows(f'{self.DAMAGED}{TARGET}</settings>\n{late}')
        self.assertEqual(rows, [('Enabled', '0')])

    def test_a_setting_inside_a_comment_is_not_read(self):
        rows, _log = status_rows(f'{self.DAMAGED}<!-- {TARGET} --></settings>')
        self.assertEqual(rows, [])

    def test_an_unfinished_tag_does_not_hide_the_next_setting(self):
        cut = '<setting id="3" name="cut" value="x"'
        rows, log = status_rows(f'<?xml version="1.0"?><settings version="1">{OTHER}{cut}{TARGET}</settings>')
        self.assertEqual(rows, [('Enabled', '0')])
        self.assertTrue(any('1 could not be read' in line for line in log))

    def test_a_setting_with_a_closing_tag_is_read(self):
        closed = TARGET.replace(' />', '></setting>')
        rows, _log = status_rows(f'{self.DAMAGED}{closed}</settings>')
        self.assertEqual(rows, [('Enabled', '0')])

    def test_the_log_names_the_user_folder(self):
        _rows, log = status_rows(f'{self.DAMAGED}{TARGET}</settings>', user='150')
        self.assertTrue(any('user 150' in line for line in log))

    def test_an_abx_file_that_does_not_decode_is_logged(self):
        with patch.object(nh, 'checkabx', return_value=True), patch.object(nh, 'abxread', side_effect=ValueError('bad')):
            rows, log = status_rows('ABX')
        self.assertEqual(rows, [])
        self.assertTrue(any('could not be read' in line for line in log))


class SnoozedDecodeFailure(unittest.TestCase):
    def test_a_file_that_fails_is_logged_and_the_next_is_read(self):
        with tempfile.TemporaryDirectory() as folder:
            bad = pathlib.Path(folder) / '0' / 'notification_policy.xml'
            good = pathlib.Path(folder) / '10' / 'notification_policy.xml'
            for path in (bad, good):
                path.parent.mkdir()
            bad.write_bytes(b'ABX\x00damaged')
            good.write_text('<notification-policy><snoozed-notifications><notification key="k" time="1700000000000" />'
                            '</snoozed-notifications></notification-policy>')
            context = SimpleNamespace(get_files_found=lambda: [str(bad), str(good)])
            with patch.object(nh, 'abxread', side_effect=ValueError('Negative string length')), patch.object(nh, 'logfunc') as log:
                _headers, rows, _source = nh.get_notificationHistory_snoozed.__wrapped__(context)
        self.assertEqual(len(rows), 1)
        self.assertTrue(any('could not be read' in call.args[0] for call in log.call_args_list))

    def test_a_failed_file_is_not_named_as_the_source(self):
        with tempfile.TemporaryDirectory() as folder:
            good = pathlib.Path(folder) / '0' / 'notification_policy.xml'
            bad = pathlib.Path(folder) / '10' / 'notification_policy.xml'
            for path in (good, bad):
                path.parent.mkdir()
            good.write_text('<notification-policy><snoozed-notifications><notification key="k" time="1700000000000" />'
                            '</snoozed-notifications></notification-policy>')
            bad.write_bytes(b'ABX\x00damaged')
            context = SimpleNamespace(get_files_found=lambda: [str(good), str(bad)])
            with patch.object(nh, 'abxread', side_effect=ValueError('bad')), patch.object(nh, 'logfunc'):
                _headers, rows, source = nh.get_notificationHistory_snoozed.__wrapped__(context)
        self.assertEqual(len(rows), 1)
        self.assertEqual(source, str(good))


if __name__ == '__main__':
    unittest.main()
