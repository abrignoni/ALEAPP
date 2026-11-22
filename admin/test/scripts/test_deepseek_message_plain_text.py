"""DeepSeek message text is stored plain, and only the report page escapes it."""
import json
import pathlib
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts import artifact_report  # pylint: disable=wrong-import-position
from scripts.artifacts import Deepseek_ChatMessages as deepseek  # pylint: disable=wrong-import-position


class FakeContext:
    def __init__(self, path):
        self.path = str(path)

    def get_files_found(self):
        return [self.path]


class DeepseekPlainTextTest(unittest.TestCase):
    def test_markup_stays_plain_in_the_row_and_escaped_on_the_page(self):
        fragments = json.dumps([{'type': 'REQUEST', 'content': '<b>a</b> & b'},
                                {'type': 'RESPONSE', 'content': 'second'}])
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / 'deepseek_chat_1.db'
            database = sqlite3.connect(path)
            database.execute('CREATE TABLE chat_session_messages_1(role TEXT, inserted_at REAL, fragments TEXT)')
            database.execute('INSERT INTO chat_session_messages_1 VALUES (?, ?, ?)', ('USER', 1000.0, fragments))
            database.commit()
            database.close()
            _, rows, _ = deepseek.deepseek_chat_messages.__wrapped__(FakeContext(path))
        self.assertEqual(rows[0][4], '<b>a</b> & b\n\nsecond')
        columns = deepseek.__artifacts_v2__['deepseek_chat_messages']['multiline_columns']
        self.assertEqual(artifact_report.cell_html(rows[0][4], 'Message Content', [], columns),
                         '&lt;b&gt;a&lt;/b&gt; &amp; b<br><br>second')

    def test_an_inserted_at_that_cannot_convert_is_shown_as_stored(self):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / 'deepseek_chat_1.db'
            database = sqlite3.connect(path)
            database.execute('CREATE TABLE chat_session_messages_1(role TEXT, inserted_at, fragments TEXT)')
            database.executemany('INSERT INTO chat_session_messages_1 VALUES (?, ?, ?)',
                                 [('USER', 2000.0, '[]'), ('USER', 'invalid', '[]'), ('USER', 'inf', '[]')])
            database.commit()
            database.close()
            _, rows, _ = deepseek.deepseek_chat_messages.__wrapped__(FakeContext(path))
        self.assertEqual(len(rows), 3)
        self.assertEqual({row[2] for row in rows[:2]}, {'invalid', 'inf'})
        self.assertEqual([row[0] for row in rows[:2]], [None, None])
        self.assertEqual(rows[2][0], 2000.0)


if __name__ == '__main__':
    unittest.main()
