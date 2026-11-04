"""Artifacts that open the first file found pick the database, not a sidecar listed before it.

Eight modules took files_found[0]. When the seeker lists a -wal or -shm ahead of its database
the artifact opened the sidecar, which raises sqlite3.DatabaseError ('file is not a database').
The database here is valid and empty, so a module that picks it fails with OperationalError
('no such table'), which is the outcome that shows it opened the right file.
"""
import importlib
import os
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import MagicMock

from scripts.context import Context

# module, a path that its pattern matches (the part after the last device folder)
MODULES = {
    'AdidasUser': 'data/com.runtastic.android/databases/user.db',
    'ChessWithFriends': 'data/com.zynga.chess/googleplay/databases/wf_database.sqlite',
    'WordsWithFriends': 'data/com.zynga.words/db/wf_database.sqlite',
    'Zapya': 'data/dewmobile.zapya/databases/transfer20.db',
    'smanagerCrash': 'data/com.samsung.android.sm/databases/sm.db',
    'smembersAppInv': 'data/com.samsung.oh/databases/com_pocketgeek_sdk_app_inventory.db',
    'smembersEvents': 'data/com.samsung.oh/databases/com_pocketgeek_sdk.db',
    'vaulty_files': 'data/com.ronrogers.vaultyfree/databases/media.db',
}


class SidecarListedFirstTest(unittest.TestCase):

    def tearDown(self):
        Context.clear()

    def run_with(self, module_name, order):
        tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmpdir, True)
        module = importlib.import_module(f'scripts.artifacts.{module_name}')
        info = module.__artifacts_v2__
        name, block = next(iter(info.items()))
        rel = MODULES[module_name]
        files = {'db': os.path.join(tmpdir, rel), 'wal': os.path.join(tmpdir, rel + '-wal'),
                 'shm': os.path.join(tmpdir, rel + '-shm')}
        os.makedirs(os.path.dirname(files['db']), exist_ok=True)
        connection = sqlite3.connect(files['db'])
        connection.execute('CREATE TABLE unrelated(x)')
        connection.commit()
        connection.close()
        for kind in ('wal', 'shm'):
            with open(files[kind], 'wb') as handle:
                handle.write(os.urandom(64))
        Context.clear()
        Context.set_data_folder(tmpdir)
        Context.set_files_found([files[k] for k in order])
        os.makedirs(os.path.join(tmpdir, 'report'), exist_ok=True)
        Context.set_report_folder(os.path.join(tmpdir, 'report'))
        Context.set_seeker(MagicMock())
        Context.set_artifact_info(block)
        try:
            getattr(module, name).__wrapped__(Context)
        except sqlite3.Error as error:
            return error
        return None

    def test_the_database_is_opened_whatever_order_the_files_are_listed_in(self):
        for module_name in MODULES:
            for order in (('db', 'wal', 'shm'), ('wal', 'shm', 'db')):
                with self.subTest(module=module_name, order=order):
                    error = self.run_with(module_name, order)
                    # OperationalError is a DatabaseError, so the message tells them apart
                    self.assertNotIn('file is not a database', str(error))


if __name__ == '__main__':
    unittest.main()
