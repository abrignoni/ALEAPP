"""galleryvault_account_profile must pair each AccountProfile.xml with the Kidd.xml
from the SAME container.

GalleryVault decrypts AccountProfile.xml with an 8-byte DES-ECB key taken from the
last_android_id in Kidd.xml. A device with more than one Android user holds one pair per
user, each with its own android_id. The artifact used to keep the last AccountProfile.xml
and the last Kidd.xml it saw independently, so on a two-user extraction it decrypted one
user's profile with the other user's key: the reported account was garbage and the second
user's account was dropped.

These tests build synthetic containers with their own keys and encrypted values (no real
evidence bytes) and assert that each container is decrypted only with its own Kidd.xml,
that the duplicate storage views of one container collapse, that a profile and Kidd in
different storage views of one container still pair, and that a container missing either
file is skipped. The two-user test fails on the pre-fix code, which cross-pairs.
"""
import json
import os
import sys
import tempfile
import unittest

from Crypto.Cipher import DES

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, REPO_ROOT)

from scripts.context import Context  # noqa: E402  pylint: disable=wrong-import-position
from scripts.artifacts.galleryVault import (  # noqa: E402  pylint: disable=wrong-import-position
    galleryvault_account_profile)

PKG = 'com.thinkyeah.galleryvault'
_ACCOUNT_PROFILE = galleryvault_account_profile.__wrapped__


def _pad(data):
    pad = 8 - (len(data) % 8)
    return data + bytes([pad]) * pad


def _encrypt(value, android_id):
    """Hex of DES-ECB(PKCS#5(value)) under the first 8 chars of android_id, as the app stores it."""
    cipher = DES.new(android_id[:8].encode('utf-8'), DES.MODE_ECB)
    return cipher.encrypt(_pad(value.encode('utf-8'))).hex()


def _kidd_xml(android_id):
    return (f"<?xml version='1.0' encoding='utf-8' standalone='yes' ?>\n"
            f'<map><string name="last_android_id">{android_id}</string></map>')


def _profile_xml(android_id, email, account_id, info):
    return (
        "<?xml version='1.0' encoding='utf-8' standalone='yes' ?>\n<map>"
        f'<string name="AccountEmail">{_encrypt(email, android_id)}</string>'
        f'<string name="AccountId">{_encrypt(account_id, android_id)}</string>'
        f'<string name="AccountInfo">{_encrypt(json.dumps(info), android_id)}</string>'
        '</map>')


# Two accounts with different keys and different values, so a cross-container pairing
# cannot accidentally look correct.
USER0 = {
    'android_id': 'aaaaaaaaaaaaaaaa',
    'email': 'zero@example.test',
    'id': '10000000',
    'info': {'name': 'Zero', 'active': True, 'is_oauth_login': True,
             'oauth_provider': 'google', 'oauth_user_email': 'zero.oauth@example.test',
             'token': '0000token0000'},
}
USER10 = {
    'android_id': 'bbbbbbbbbbbbbbbb',
    'email': 'ten@example.test',
    'id': '20000000',
    'info': {'name': 'Ten', 'active': False, 'is_oauth_login': False,
             'oauth_provider': '', 'oauth_user_email': '', 'token': '1010token1010'},
}


class GalleryVaultAccountProfileTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_folder = os.path.join(self.tmp.name, 'report', 'data')
        Context.set_data_folder(self.data_folder)
        self.files = []

    def tearDown(self):
        Context.clear()
        self.tmp.cleanup()

    def _stage(self, relative, text):
        """Write a shared_prefs file at data_folder/<relative>, record its staged path."""
        full = os.path.join(self.data_folder, relative)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8') as handle:
            handle.write(text)
        self.files.append(full)

    def _prefs_dir(self, storage_view):
        return f'{storage_view}/{PKG}/shared_prefs'

    def _add_account(self, storage_view, account, both=True, kidd=True, profile=True):
        prefs = self._prefs_dir(storage_view)
        if kidd:
            self._stage(f'{prefs}/Kidd.xml', _kidd_xml(account['android_id']))
        if profile:
            self._stage(f'{prefs}/AccountProfile.xml',
                        _profile_xml(account['android_id'], account['email'],
                                     account['id'], account['info']))
        _ = both

    def _run(self):
        Context.set_files_found(list(self.files))
        headers, rows, source_path = _ACCOUNT_PROFILE(Context)
        return headers, rows, source_path

    def _by_user(self, rows):
        """{user: {name: value}} from the (user, name, value) rows."""
        out = {}
        for user, name, value in rows:
            out.setdefault(user, {})[name] = value
        return out

    def test_two_users_each_decrypts_with_its_own_key(self):
        # Files interleaved so a last-AccountProfile / last-Kidd accessor cross-pairs.
        self._add_account('data/user/10', USER10)
        self._add_account('data/data', USER0)
        headers, rows, source_path = self._run()

        self.assertEqual(headers, ('Android User', 'Name', 'Value'))
        self.assertEqual(len(rows), 16, 'expected 8 rows for each of the two users')
        by_user = self._by_user(rows)
        self.assertEqual(set(by_user), {'0', '10'})

        # Each user's fields decrypt to that user's own plaintext, never the other's.
        # On the pre-fix code user 0's profile was decrypted with user 10's key, so these
        # equalities fail (the value is replacement-character garbage).
        self.assertEqual(by_user['0']['Account Email'], USER0['email'])
        self.assertEqual(by_user['0']['Account ID'], USER0['id'])
        self.assertEqual(by_user['0']['Account Name'], 'Zero')
        self.assertEqual(by_user['0']['OAuth Provider'], 'google')
        self.assertEqual(by_user['0']['Account Token'], '0000token0000')
        self.assertEqual(by_user['10']['Account Email'], USER10['email'])
        self.assertEqual(by_user['10']['Account ID'], USER10['id'])
        self.assertEqual(by_user['10']['Account Name'], 'Ten')
        self.assertEqual(by_user['10']['OAuth Login'], 'False')

        # Neither user's account leaks into the other's rows.
        self.assertNotEqual(by_user['0']['Account Email'], by_user['10']['Account Email'])

        # Every file that produced a row is named in the source path, none twice.
        cited = source_path.split('\n')
        self.assertEqual(len(cited), 4)
        self.assertEqual(len(set(cited)), 4)
        for path in cited:
            self.assertTrue(path.endswith(('AccountProfile.xml', 'Kidd.xml')))

    def test_single_container_yields_one_account(self):
        self._add_account('data/data', USER0)
        _headers, rows, _source_path = self._run()
        by_user = self._by_user(rows)
        self.assertEqual(set(by_user), {'0'})
        self.assertEqual(len(rows), 8)
        self.assertEqual(by_user['0']['Account Email'], USER0['email'])

    def test_duplicate_storage_views_collapse(self):
        # One user under all three credential-encrypted spellings must not multiply rows.
        for view in ('data/data', 'data/user/0', 'data_mirror/data_ce/null/0'):
            self._add_account(view, USER0)
        _headers, rows, source_path = self._run()
        self.assertEqual(len(rows), 8, 'the three storage views of one container must collapse')
        self.assertEqual(self._by_user(rows)['0']['Account Email'], USER0['email'])
        # Only the kept copy of each file is cited.
        self.assertEqual(len(source_path.split('\n')), 2)

    def test_profile_and_kidd_in_different_views_pair(self):
        # A profile in one storage view and its Kidd in another view of the SAME user
        # must still pair; the container key is the user, not the on-disk directory.
        self._stage(f'{self._prefs_dir("data/user/10")}/AccountProfile.xml',
                    _profile_xml(USER10['android_id'], USER10['email'],
                                 USER10['id'], USER10['info']))
        self._stage(f'{self._prefs_dir("data_mirror/data_ce/null/10")}/Kidd.xml',
                    _kidd_xml(USER10['android_id']))
        _headers, rows, _source_path = self._run()
        by_user = self._by_user(rows)
        self.assertEqual(set(by_user), {'10'})
        self.assertEqual(by_user['10']['Account Email'], USER10['email'])

    def test_container_missing_a_file_is_skipped(self):
        self._add_account('data/user/11', USER0, profile=True, kidd=False)   # profile only
        self._add_account('data/user/12', USER10, profile=False, kidd=True)  # kidd only
        _headers, rows, source_path = self._run()
        self.assertEqual(rows, [], 'a container without both files cannot be decrypted')
        self.assertEqual(source_path, '')


if __name__ == '__main__':
    unittest.main()
