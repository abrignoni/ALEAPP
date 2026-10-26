"""Write-ahead log recovery in artifacts must find the log beside a path with a space.

scripts/sqlite_wal.py takes a file system path and builds its own SQLite URI. A path that
has already been turned into a URI fragment (get_sqlite_db_path percent-encodes spaces) is
not a file name: the reader then sees no -wal and recovers nothing, without an error.
Every database here sits in a folder whose name has a space, as a case folder often does.
"""
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest


ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.artifacts import phoneLink, snapchat  # pylint: disable=wrong-import-position


def _capture(folder, name, statements):
    """Run statements in WAL mode and copy the database and its log out while the writer
    is still open, since closing it checkpoints the log away."""
    live = os.path.join(folder, 'live')
    evidence = os.path.join(folder, 'case folder with space')
    os.makedirs(live)
    os.makedirs(evidence)
    connection = sqlite3.connect(os.path.join(live, name), isolation_level=None)
    connection.execute('PRAGMA journal_mode=WAL')
    connection.execute('PRAGMA wal_autocheckpoint=0')
    for statement in statements:
        connection.execute(statement)
    for suffix in ('', '-wal'):
        shutil.copyfile(os.path.join(live, name + suffix), os.path.join(evidence, name + suffix))
    connection.close()
    return os.path.join(evidence, name)


class WalRecoveryPathTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_snapchat_messages_found_beside_a_path_with_a_space(self):
        path = _capture(self.tmp, 'arroyo.db', [
            'CREATE TABLE m (conv TEXT, id INTEGER, txt TEXT)',
            "INSERT INTO m VALUES ('c', 1, 'kept')",
            "INSERT INTO m VALUES ('c', 2, 'removed')",
            'DELETE FROM m WHERE id = 2'])
        removed = snapchat._removed_in_log(  # pylint: disable=protected-access
            path, 'SELECT conv, id, txt FROM m', (0, 1), {('c', 1)})
        self.assertEqual([row for row, _spans in removed], [('c', 2, 'removed')])

    def test_snapchat_conversations_found_beside_a_path_with_a_space(self):
        path = _capture(self.tmp, 'arroyo.db', [
            'CREATE TABLE conversation (client_conversation_id TEXT)',
            'CREATE TABLE feed_entry (client_conversation_id TEXT)',
            "INSERT INTO conversation VALUES ('kept')",
            "INSERT INTO conversation VALUES ('gone')",
            "DELETE FROM conversation WHERE client_conversation_id = 'gone'"])
        removed = snapchat._removed_conversation_ids(path)  # pylint: disable=protected-access
        self.assertEqual(set(removed), {'gone'})

    def test_phone_link_events_found_beside_a_path_with_a_space(self):
        path = _capture(self.tmp, 'eventstore', [
            'CREATE TABLE content_access_event (uid INTEGER PRIMARY KEY, start_time INTEGER)',
            'INSERT INTO content_access_event VALUES (1, 1)',
            'INSERT INTO content_access_event VALUES (2, 2)',
            'DELETE FROM content_access_event WHERE uid = 2'])
        rows = phoneLink._read_states(  # pylint: disable=protected-access
            path, 'SELECT uid, start_time FROM content_access_event', 0)
        self.assertEqual({uid: label for uid, (_row, label, _location) in rows.items()},
                         {1: phoneLink.CURRENT_STATE, 2: phoneLink.OTHER_STATE})

if __name__ == '__main__':
    unittest.main()
