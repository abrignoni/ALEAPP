"""Stored mobile values and SQLite types survive without truthiness substitution."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from scripts.artifacts import Deepseek_UserInfo as deepseek
from admin.test.scripts.test_history_doclist_all_sources import Context

VALUES = [None, '', ' ', '\u00a0', 0, 0.0, '0', 'None', 'Not Found', '+44 <é>:123', '+44 <é>:123']


def create_deepseek_fixture(root, empty=False):
    path = Path(root)/'data/data/com.deepseek.chat/databases/deepseek_chat.db'
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE app_user_info(id,token,email,mobile_number)')
    if not empty:
        db.executemany('INSERT INTO app_user_info VALUES (?,?,?,?)',
                       [(1, 'constructed-token', 'user@example.test', value) for value in VALUES])
    db.commit()
    db.close()
    return path


class TestDeepseekMobileValues(unittest.TestCase):
    def test_values_types_and_duplicate_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path = create_deepseek_fixture(directory)
            _, rows, source = deepseek.deepseek_user_info.__wrapped__(Context(directory, [str(path)]))
            db = sqlite3.connect(path)
            expected = db.execute('SELECT id,token,email,mobile_number FROM app_user_info').fetchall()
            db.close()
            self.assertEqual(rows, expected)
            self.assertEqual([type(row[3]) for row in rows], [type(value) for value in VALUES])
            self.assertEqual(rows[-1], rows[-2])
            self.assertEqual(source, str(path))

    def test_empty_table_has_no_fabricated_row(self):
        with tempfile.TemporaryDirectory() as directory:
            path = create_deepseek_fixture(directory, empty=True)
            self.assertEqual(deepseek.deepseek_user_info.__wrapped__(Context(directory, [str(path)]))[1], [])
