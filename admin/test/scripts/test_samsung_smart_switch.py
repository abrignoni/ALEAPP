"""Smart Switch parsers read a synthetic com.sec.android.easyMover tree."""
import datetime
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from smart_switch_fixture import APP, T0, make_tree, write_json  # pylint: disable=wrong-import-position
from scripts.artifacts import samsungSmartSwitch as ss  # pylint: disable=wrong-import-position

UTC = datetime.timezone.utc
START = datetime.datetime(2026, 1, 1, tzinfo=UTC)


def context(root, paths):
    return SimpleNamespace(
        get_files_found=lambda: [str(path) for path in paths],
        get_relative_path=lambda path: str(pathlib.Path(path).relative_to(root)))


def named(headers, row):
    return dict(zip([h if isinstance(h, str) else h[0] for h in headers], row))


class SmartSwitchTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = pathlib.Path(self.folder.name)
        self.paths = make_tree(self.root)

    def go(self, parser, paths=None):
        with patch.object(ss, 'logfunc'):
            return parser.__wrapped__(context(self.root, paths or self.paths))

    def test_sessions_merge_files_collapse_views_and_keep_users_apart(self):
        headers, rows, source = self.go(ss.smartswitch_sessions)
        self.assertTrue(all(len(row) == len(headers) for row in rows))
        self.assertEqual([(r[0], r[1]) for r in rows],
                         [('0', str(T0)), ('0', str(T0 + 3600000)), ('10', str(T0))])
        first = named(headers, rows[0])
        self.assertEqual(first['History Folder Time'], START)
        self.assertEqual((first['Service Type'], first['Sender Type'], first['State']),
                         ('AccessoryD2d', 'Receiver', 'Complete'))
        self.assertEqual((first['Model Name'], first['OS Version'], first['One UI Version']),
                         ('SM-TEST1', '36', 80000))
        self.assertEqual((first['Account Count'], first['Item Count']), (2, 3 - 1))
        self.assertEqual(first['Completed Service Flag'], 1025)
        second = named(headers, rows[1])
        self.assertEqual((second['Sender Type'], second['Model Name'], second['Item Count']),
                         ('', 'SM-TEST1', ''))
        other = named(headers, rows[2])
        self.assertEqual((other['Sender Type'], other['Model Name'], other['Account Count']),
                         ('Sender', '', ''))
        self.assertEqual(len(source.splitlines()), 5)

    def test_items(self):
        headers, rows, _ = self.go(ss.smartswitch_items)
        self.assertEqual([r[3] for r in rows], ['CONTACT', 'MEDIASEARCH'])
        contact = named(headers, rows[0])
        self.assertEqual((contact['Status'], contact['Content Count'], contact['Restore Result'],
                          contact['Restore Response Result'], contact['Backup Step']),
                         ('COMPLETED', 5, 'Yes', 0, 'Backup'))
        empty = named(headers, rows[1])
        self.assertEqual((empty['Backup Time'], empty['Restore Result'], empty['Restore Error'],
                          empty['Backup Result']), (-1, 'No', 'failed', ''))

    def test_peer_lists(self):
        headers, rows, _ = self.go(ss.smartswitch_peer_apps)
        self.assertEqual(len(rows), 4)
        first = named(headers, rows[0])
        self.assertEqual((first['Package'], first['Runtime Permissions']), ('com.example.contacts', 2))
        self.assertEqual(first['Last Time Used'], START - datetime.timedelta(seconds=5))
        second = named(headers, rows[1])
        self.assertEqual((second['Last Time Used'], second['Runtime Permissions'],
                          second['Support Stub Install']), ('', '', 'No'))
        _, accounts, _ = self.go(ss.smartswitch_peer_accounts)
        self.assertEqual([r[3:] for r in accounts[:2]],
                         [('com.example.chat', 'user-a'), ('com.google', '')])
        headers, messages, _ = self.go(ss.smartswitch_peer_messages)
        self.assertEqual(len(messages), 4)
        self.assertEqual(named(headers, messages[0])['SMS Count'], 20)
        headers, contacts, _ = self.go(ss.smartswitch_peer_contacts)
        self.assertEqual([named(headers, r)['List'] for r in contacts[:2]],
                         ['AllContactAccounts', 'ContactAccounts'])
        self.assertEqual(named(headers, contacts[0])['Selected'], 'Yes')

    def test_transferred_history_and_backup_media(self):
        _, rows, _ = self.go(ss.smartswitch_transferred_history)
        self.assertEqual(rows, [('0', '00000000-1111-2222-3333-444444444444', 'Test phone',
                                 START + datetime.timedelta(milliseconds=3600052))])
        headers, media, _ = self.go(ss.smartswitch_backup_media)
        self.assertEqual([r[1:4] for r in media],
                         [(1, 'a.jpg', '/sdcard/a.jpg'), (2, 'b.mp4', '/sdcard/b.mp4')])
        self.assertEqual(len(headers), len(media[0]))

    def test_unreadable_json_and_wrong_shapes(self):
        bad = self.root / APP / 'History' / '1' / 'objItems.json'
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.write_text('{broken', encoding='utf-8')
        odd = write_json(self.root / APP / 'History' / '2' / 'peerDeviceInfo.json',
                         {'AccountInfos': 5, 'CategoryInfoExtra': {'a': 1}, 'MessagePeriods': None,
                          'AllContactAccounts': [7]})
        for parser in (ss.smartswitch_items, ss.smartswitch_peer_apps, ss.smartswitch_peer_accounts,
                       ss.smartswitch_peer_messages, ss.smartswitch_peer_contacts):
            _, rows, _ = self.go(parser, [bad, odd])
            self.assertEqual(rows, [], parser.__name__)
        _, sessions, _ = self.go(ss.smartswitch_sessions, [bad, odd])
        self.assertEqual([r[1] for r in sessions], ['1', '2'])

    def test_time_helper(self):
        # pylint: disable=protected-access
        self.assertEqual(ss._ms(T0), START)
        for value in (None, '', 0, -5, 'x', True, 10 ** 30):
            self.assertEqual(ss._ms(value), '')
        self.assertEqual(ss._history_ms('abc'), '')


if __name__ == '__main__':
    unittest.main()
