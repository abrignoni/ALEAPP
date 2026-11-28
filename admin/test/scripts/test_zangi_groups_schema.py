"""Zangi Groups on a t_group with and without g_is_accepted. Values are made up for the test."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts.ZangiChats import zangi_groups  # pylint: disable=wrong-import-position


def make_database(path, with_accepted):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    accepted = ', g_is_accepted INT' if with_accepted else ''
    db.execute(f'CREATE TABLE t_group (g_group_id INTEGER PRIMARY KEY, g_name TEXT, g_uid TEXT, '
               f'g_state INT, g_type INT{accepted})')
    db.execute('CREATE TABLE t_chat_members (m_id INTEGER PRIMARY KEY, m_chatjid TEXT, '
               'm_member_group_id BIGINT, m_memberrole INT)')
    db.execute('CREATE TABLE t_conversation (c_group_id BIGINT, c_last_update_date BIGINT)')
    values = (1, 'Group', 'uid1', 0, 1) + ((2,) if with_accepted else ())
    db.execute(f'INSERT INTO t_group VALUES ({",".join("?" * len(values))})', values)
    db.execute("INSERT INTO t_chat_members VALUES (1, 'member', 1, 3)")
    db.execute('INSERT INTO t_conversation VALUES (1, 1700000000123)')
    db.commit()
    db.close()


class ZangiGroupsSchemaTest(unittest.TestCase):
    def run_groups(self, with_accepted):
        with tempfile.TemporaryDirectory() as root:
            path = pathlib.Path(root) / 'data' / 'data' / 'com.beint.zangi' / 'databases' / '1.db'
            make_database(path, with_accepted)
            context = SimpleNamespace(get_files_found=lambda: [str(path)], get_relative_path=str)
            headers, rows, _source = zangi_groups.__wrapped__(context)
        names = [header[0] if isinstance(header, tuple) else header for header in headers]
        return [dict(zip(names, row)) for row in rows]

    def test_with_g_is_accepted(self):
        rows = self.run_groups(True)
        self.assertEqual([(r['Group Name'], r['Member Rows'], r['g_is_accepted (as stored)']) for r in rows],
                         [('Group', 1, 2)])

    def test_without_g_is_accepted_the_group_is_still_reported(self):
        rows = self.run_groups(False)
        self.assertEqual([(r['Group Name'], r['Member Rows'], r['g_is_accepted (as stored)']) for r in rows],
                         [('Group', 1, '')])


if __name__ == '__main__':
    unittest.main()
