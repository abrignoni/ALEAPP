"""Key selection for the Samsung encrypted stores: per-user keys, user-less keys, and refusal."""
import json
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import samsungSecureStores as module  # pylint: disable=wrong-import-position

HEALTH_KEY = "x'" + '11' * 32 + '22' * 16 + "'"
OTHER_KEY = "x'" + '33' * 32 + '22' * 16 + "'"


def make_tree(root, users, entries):
    paths = []
    for user_dir in users:
        db = pathlib.Path(root) / user_dir / 'com.sec.android.app.shealth/databases/SecureHealthData.db'
        db.parent.mkdir(parents=True, exist_ok=True)
        db.write_bytes(b'\x22' * 16 + b'\x00' * 4080)
        paths.append(db)
    secrets = pathlib.Path(root) / 'extra/Secrets/secrets.json'
    secrets.parent.mkdir(parents=True, exist_ok=True)
    secrets.write_text(json.dumps(entries))
    paths.append(secrets)
    return paths


def entry(user_id, key):
    item = {'app': module.HEALTH, 'script_title': 'test', 'script_output': [{'payload': {'SecureHealthData': key}}]}
    if user_id is not None:
        item['user_id'] = user_id
    return item


def fake_decrypt(good_key):
    """Accept only good_key; write a one-table plaintext database like the real helper would."""
    def decrypt(_path, key, output, **_kwargs):
        if key != good_key:
            pathlib.Path(output).write_bytes(b'garbage')
            return 1, 0
        pathlib.Path(output).unlink(missing_ok=True)  # the real helper rewrites its output whole
        con = sqlite3.connect(output)
        con.execute('CREATE TABLE com_samsung_health_sleep(com_samsung_health_sleep_start__time INTEGER)')
        con.execute('INSERT INTO com_samsung_health_sleep VALUES (1794801600000)')
        con.commit()
        con.close()
        return 1, 1
    return decrypt


class SamsungSecureStoresTest(unittest.TestCase):
    def setUp(self):
        module._decrypted.clear()  # pylint: disable=protected-access

    def run_case(self, users, entries):
        with tempfile.TemporaryDirectory() as root:
            files = make_tree(root, users, entries)
            report = pathlib.Path(root) / 'report'
            report.mkdir()
            context = SimpleNamespace(get_files_found=lambda: [str(p) for p in files],
                                      get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)),
                                      get_report_folder=lambda: str(report))
            logs = []
            with mock.patch.object(module, 'decrypt_sqlcipher_db', fake_decrypt(bytes.fromhex('11' * 32))), \
                    mock.patch.object(module, 'logfunc', logs.append):
                found = module._databases(context, module.HEALTH, 'SecureHealthData.db')  # pylint: disable=protected-access
                users_opened = sorted(user for _out, _src, user in found)
                leftovers = sorted(p.name for p in (report / 'samsung_secure_decrypted').glob('*')) \
                    if (report / 'samsung_secure_decrypted').exists() else []
            return users_opened, logs, leftovers

    def test_key_for_the_matching_user_only(self):
        opened, logs, _ = self.run_case(['data/data', 'data/user/10'], [entry(0, HEALTH_KEY)])
        self.assertEqual(opened, ['0'])
        self.assertTrue(any('Android user 10' in line for line in logs))

    def test_userless_key_is_tried_and_must_authenticate(self):
        opened, _, _ = self.run_case(['data/data'], [entry(None, OTHER_KEY), entry(None, HEALTH_KEY)])
        self.assertEqual(opened, ['0'])

    def test_wrong_key_is_refused_and_its_output_removed(self):
        opened, logs, leftovers = self.run_case(['data/data'], [entry(0, OTHER_KEY)])
        self.assertEqual(opened, [])
        self.assertEqual(leftovers, [])
        self.assertTrue(any('authenticated' in line for line in logs))

    def test_raw_key_literal_shape(self):
        self.assertEqual(module._encryption_key(module.HEALTH, HEALTH_KEY, None),  # pylint: disable=protected-access
                         bytes.fromhex('11' * 32))
        self.assertIsNone(module._encryption_key(module.HEALTH, 'not a key', None))  # pylint: disable=protected-access


if __name__ == '__main__':
    unittest.main()
