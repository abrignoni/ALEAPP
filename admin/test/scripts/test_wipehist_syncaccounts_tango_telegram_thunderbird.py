"""Record grouping, per-database reading and stored-value columns (constructed inputs only)."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.artifacts import sWipehist, syncAccounts, tangomessage, telegramAndroid, thunderbird


def context(root, paths):
    return SimpleNamespace(get_files_found=lambda: [str(p) for p in paths],
                           get_relative_path=lambda p: str(Path(p).relative_to(root)))


HISTORY = ('+ [AA | 2020/01/02 03:04:05 | BUILD]\n--wipe_data\n--requested_time=2020/01/02 03:04:00\n'
           '--reason=one\n--locale=en-US\nreboot reason: old spelling\n'
           '+ [AA | 2020/02/02 03:04:05 | BUILD]\n--update_package=x\n--locale=en-GB\nreboot_reason=two\n'
           '+ [AA | 2020/03/02 03:04:05 | BUILD]\n--prompt_and_wipe_data\n--reason=three\nreboot_reason=four\n'
           '+ [AA | 2020/04/02 03:04:05 | BUILD]\n--wipe_data\n--reason=cut short\n')


class TestWipeHistoryRecords(unittest.TestCase):
    def test_each_record_keeps_its_own_values_and_a_copy_is_reported_once(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = root / 'efs/recovery/history'
            second = root / 'data/log/recovery_history.log'
            for path, text in ((first, HISTORY), (second, HISTORY + HISTORY.split('+')[1].join(['+', '']))):
                path.parent.mkdir(parents=True)
                path.write_text(text, encoding='utf-8')
            headers, rows, source = sWipehist.get_sWipehist.__wrapped__(context(root, [first, second]))
            self.assertEqual(headers[1:3], ('--wipe_data', '--prompt_and_wipe_data'))
            self.assertEqual(source, f'{first}\n{second}')
            self.assertEqual(rows[:3], [
                ('2020-01-02 03:04:05', 'Yes', '', 'one\n', ' old spelling\n', 'en-US\n', '2020-01-02 03:04:00\n'),
                ('2020-03-02 03:04:05', '', 'Yes', 'three\n', 'four\n', '', ''),
                ('2020-04-02 03:04:05', 'Yes', '', 'cut short\n', '', '', ''),
            ])
            # The second file repeats the first record once more than the first file holds it.
            self.assertEqual(len(rows), 4)
            self.assertEqual(rows[3][0], '2020-01-02 03:04:05')


class TestSyncAccountsSources(unittest.TestCase):
    def test_mirror_is_judged_on_the_extraction_path_and_every_source_is_named(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'data_mirror case'
            xml = '<accounts><authority id="1" user="0" account="a" type="t" authority="x" enabled="true" syncable="1"/></accounts>'
            paths = []
            for relative in ('data/system/sync/accounts.xml', 'other/system/sync/accounts.xml',
                             'data_mirror/x/system/sync/accounts.xml'):
                path = root / relative
                path.parent.mkdir(parents=True)
                path.write_text(xml, encoding='utf-8')
                paths.append(path)
            _, rows, source = syncAccounts.syncAccountsXml.__wrapped__(context(root, paths))
            self.assertEqual(len(rows), 2)
            self.assertEqual(source, f'{paths[0]}\n{paths[1]}')


class TestTangoPayload(unittest.TestCase):
    def test_non_ascii_text_is_kept_and_a_missing_id_is_none(self):
        import base64
        payload = base64.b64encode(b'\x0a\x03cid\x12' + 'café 你好'.encode('utf-8') + b'cid\xff')
        self.assertEqual(tangomessage._decodeMessage('cid', payload),  # pylint: disable=protected-access
                         '\x12café 你好')
        self.assertIsNone(tangomessage._decodeMessage('zzz', payload))  # pylint: disable=protected-access
        self.assertIsNone(tangomessage._decodeMessage('cid', None))  # pylint: disable=protected-access


class TestTelegramMains(unittest.TestCase):
    def make(self, root, relative, pinned):
        path = root / relative
        path.parent.mkdir(parents=True)
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE users(uid, name, status)')
            db.execute('CREATE TABLE user_settings(uid, info, pinned)')
            db.execute("INSERT INTO users VALUES(7, ?, 0)", (relative[-20:] + ';;;u',))
            db.execute('INSERT INTO user_settings VALUES(7, NULL, ?)', (pinned,))
        return path

    def test_one_copy_per_user_and_account_folder_with_stored_pinned(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pkg = 'org.telegram.messenger'
            main = self.make(root, f'data/data/{pkg}/files/cache4.db', 0)
            view = self.make(root, f'data/user/0/{pkg}/files/cache4.db', 0)
            mirror = self.make(root, f'data_mirror/data_ce/null/0/{pkg}/files/cache4.db', 0)
            slot = self.make(root, f'data/data/{pkg}/files/account2/cache4.db', 55)
            user10 = self.make(root, f'data/user/10/{pkg}/files/cache4.db', None)
            self.make(root, f'data/data/{pkg}/files/account4/cache4.db', 1)
            self.make(root, 'data/data/other.app/files/cache4.db', 1)
            everything = sorted(root.rglob('cache4.db'))
            headers, rows, source = telegramAndroid.get_telegramPeerDetails.__wrapped__(
                context(root, [main, view, mirror, slot, user10] + everything))
            self.assertEqual(headers[-2:], ('pinned (as stored)', 'Source File'))
            self.assertEqual(source, f'{main}\n{slot}\n{user10}')
            self.assertEqual([(r[1], r[5], r[6]) for r in rows], [
                ('nger/files/cache4.db', 0, str(main.relative_to(root))),
                ('s/account2/cache4.db', 55, str(slot.relative_to(root))),
                ('nger/files/cache4.db', None, str(user10.relative_to(root))),
            ])
            headers, rows, source = telegramAndroid.get_telegramPeerDetails.__wrapped__(
                context(root, [view, main]))
            self.assertEqual((len(headers), len(rows), source), (6, 1, str(view)))
            headers, rows, source = telegramAndroid.get_telegramUsers.__wrapped__(context(root, []))
            self.assertEqual((len(headers), rows, source), (5, [], ''))


class TestTelegramAutoDownloadKeys(unittest.TestCase):
    def test_current_values_and_numbered_presets_are_reported_as_stored(self):
        preset = '1_2_4_8_10_20_30_40_1_0_1'
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'mainconfig.xml'
            path.write_text(f'<map><string name="mobilePreset">{preset}</string>'
                            f'<string name="preset1">{preset}</string>'
                            '<int name="currentMobilePreset" value="1"/></map>', encoding='utf-8')
            headers, rows, _ = telegramAndroid.get_telegramAutoDownload.__wrapped__(
                SimpleNamespace(get_files_found=lambda: [str(path)]))
            self.assertEqual(headers[:3], ('Preference Key', 'Network', 'Current Preset Key (as stored)'))
            self.assertEqual([r[:5] for r in rows[::4]], [
                ('mobilePreset', 'Mobile data', '1', 'Yes', 'Contacts'),
                ('preset1', '', '', 'Yes', 'Contacts')])
            self.assertEqual(len(rows), 8)


class TestThunderbirdEveryPreferencesFile(unittest.TestCase):
    def make(self, root, relative, uuid, address):
        path = root / relative
        path.parent.mkdir(parents=True)
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE preferences_storage(primkey, value)')
            db.executemany('INSERT INTO preferences_storage VALUES(?,?)', [
                (uuid + '.email.0', address),
                (uuid + '.incomingServerSettings', json.dumps({'username': 'u', 'password': 'p', 'host': 'h'}))])
        return path

    def test_second_user_is_read_and_a_storage_view_copy_is_not_repeated(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            tail = 'net.thunderbird.android/databases/preferences_storage'
            first = self.make(root, 'data/data/' + tail, '1' * 8 + '-1111-1111-1111-' + '1' * 12, 'a@example.test')
            copy = self.make(root, 'data/user/0/' + tail, '1' * 8 + '-1111-1111-1111-' + '1' * 12, 'a@example.test')
            second = self.make(root, 'data/user/10/' + tail, '2' * 8 + '-2222-2222-2222-' + '2' * 12, 'b@example.test')
            found = SimpleNamespace(get_files_found=lambda: [str(first), str(copy), str(second)])
            with patch.object(thunderbird.Context, 'get_relative_path',
                              side_effect=lambda p: str(Path(p).relative_to(root))):
                headers, rows, source = thunderbird.thunderbird_accounts.__wrapped__(found)
            self.assertEqual(headers[-1], 'Source File')
            self.assertEqual([(r[2], r[-1]) for r in rows], [
                ('a@example.test', str(first.relative_to(root))),
                ('b@example.test', str(second.relative_to(root)))])
            self.assertEqual(source, f'{first}\n{second}')


if __name__ == '__main__':
    unittest.main()
