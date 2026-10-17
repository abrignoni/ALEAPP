"""SQLite URIs built from a path keep working when the path holds '#' or '?'.

A URI such as f"file:{path}?mode=ro" ends the path at the first '#' (fragment) or
'?' (query). For a folder named "case #12" SQLite then opens "case " instead and the
tables read as absent. Each reader below must percent-quote the path, so it reads
the synthetic database it was given and leaves no stray file next to the folder.
"""
# pylint: disable=protected-access

import hashlib
import os
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import simplexChat  # pylint: disable=wrong-import-position
from scripts.artifacts import weChat  # pylint: disable=wrong-import-position


def _write_plain_db(path):
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE synthetic (value TEXT)')
        db.execute("INSERT INTO synthetic VALUES ('row')")
    db.close()


class SpecialCharacterPathTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        # "case " is where an unquoted URI for "case #1?x/..." lands.
        self.folder = os.path.join(self.root, 'case #1?x')
        os.makedirs(self.folder)
        self.stray = os.path.join(self.root, 'case ')

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def assert_no_stray(self):
        self.assertFalse(os.path.exists(self.stray), 'the URI was cut at # or ?')

    def test_wechat_opens_database_by_quoted_uri(self):
        # Plain sqlite3 stands in for sqlcipher3: both parse the URI the same way,
        # and plain SQLite ignores the cipher pragmas, so the open reaches the file.
        uin = '12345'
        account = os.path.join(self.folder, hashlib.md5(f'mm{uin}'.encode()).hexdigest())
        os.makedirs(account)
        path = os.path.join(account, 'EnMicroMsg.db')
        _write_plain_db(path)
        with patch.object(weChat, 'sqlcipher', sqlite3, create=True):
            connection = weChat._open_database(path, uin, ['synthetic'])
        self.assertIsNotNone(connection)
        try:
            self.assertEqual(connection.execute('SELECT value FROM synthetic').fetchall(), [('row',)])
        finally:
            connection.close()
        self.assert_no_stray()

    def test_simplex_opens_its_decrypted_copy(self):
        # The decrypted copy goes under the system temp folder, so a '#' there is
        # what puts the character in the path.
        def fake_decrypt(_source, _passphrase, output, **_kwargs):
            _write_plain_db(output)
            return 1, 1

        source = os.path.join(self.folder, 'simplex_v1_chat.db')
        with patch.object(tempfile, 'tempdir', self.folder), \
                patch.object(simplexChat, 'decrypt_sqlcipher_db', fake_decrypt):
            connection = simplexChat._open_decrypted(source, 'synthetic')
        self.assertIsNotNone(connection)
        try:
            self.assertEqual(connection.execute('SELECT value FROM synthetic').fetchall(), [('row',)])
        finally:
            connection.close()
        self.assert_no_stray()


if __name__ == '__main__':
    unittest.main()
