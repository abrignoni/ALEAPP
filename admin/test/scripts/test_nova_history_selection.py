"""Selected text follows recorded time while undated and empty histories survive."""
from pathlib import Path
import datetime
import shutil
import sqlite3
import tempfile
import unittest
from scripts.artifacts import AIChatbotNovaHistory as nova
from admin.test.scripts.test_history_doclist_all_sources import Context


def create_nova_history_fixture(root):
    root = Path(root)
    files = []
    for user in [0, 10]:
        path = root/f'data/user/{user}/com.scaleup.chatai/databases/chat-ai.db'
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE History (id INTEGER PRIMARY KEY, UUID, title, chatBotModel, '
                       'assistantId, captionHistoryId, starred, softDeleted, syncState, '
                       'syncRetryCount, createdAt, updatedAt, lastModifiedAt)')
            db.execute('CREATE TABLE HistoryDetail (id INTEGER PRIMARY KEY, historyID, '
                       'type, text, createdAt)')
            for ident in range(1, 8):
                db.execute('INSERT INTO History VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                           (ident, f'uuid-{ident}', f'user{user} <history>', 0, 0, None,
                            0, 0, 0, 0, 1700000000000+ident, 1700000000000,
                            1700000000000))
            # Reversed insertion and lexical/time order; undated text sorts lower.
            rows = [(12, 1, 0, 'a later', 1700000002000),
                    (13, 1, 0, '0 undated', None),
                    (11, 1, 0, f'z earlier user{user}', 1700000001000),
                    (14, 1, 1, 'assistant first', 1700000000000),
                    (22, 2, 0, 'a tie high ID', 1700000001000),
                    (21, 2, 0, 'z tie low ID', 1700000001000),
                    (32, 3, 0, 'a undated high ID', None),
                    (31, 3, 0, 'z undated low ID', None),
                    (51, 5, 1, 'assistant only', 1700000001000),
                    (61, 6, 0, None, 1700000001000),
                    (71, 7, 0, '', 1700000001000)]
            db.executemany('INSERT INTO HistoryDetail VALUES (?,?,?,?,?)', rows)
        db.close()
        files.append(path)
    alias = root/'data/data/com.scaleup.chatai/databases/chat-ai.db'
    alias.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(files[0], alias)
    files.append(alias)
    return files


class TestNovaHistorySelection(unittest.TestCase):
    def test_chronology_null_fallback_ties_and_source_multiplicity(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_nova_history_fixture(directory)
            headers, raw, sources = nova.nova_chatbot_history.__wrapped__(Context(directory, files))
            self.assertEqual([h[0] for h in headers[:5]], ['Created At', 'Updated At',
                             'Last Modified At', 'Last Message At', 'Selected User Message At'])
            labels = [h[0] if isinstance(h, tuple) else h for h in headers]
            rows = [dict(zip(labels, row)) for row in raw]
            self.assertEqual(len(rows), 14)
            self.assertEqual(len(sources.splitlines()), 2)
            expected = {1: (11, 4), 2: (21, 2), 3: (31, 2), 4: ('', 0),
                        5: ('', 1), 6: (61, 1), 7: (71, 1)}
            for row in rows:
                ident = row['Conv ID']
                self.assertEqual((row['Selected User Message ID'], row['Message Count']),
                                 expected[ident])
                source = row['Source File']
                self.assertFalse(Path(source).is_absolute())
                self.assertTrue((Path(directory)/source).is_file())
                if ident == 1:
                    user = 10 if '/10/' in source else 0
                    self.assertEqual(row['Selected User Message'], f'z earlier user{user}')
                    self.assertEqual(row['Last Message At'], datetime.datetime.fromtimestamp(1700000002, datetime.timezone.utc))
                if ident == 2:
                    self.assertEqual(row['Selected User Message'], 'z tie low ID')
                if ident == 3:
                    self.assertEqual(row['Selected User Message'], 'z undated low ID')
                    self.assertEqual(row['Selected User Message At'], '')
                    self.assertEqual(row['Selection Basis'], 'lowest ID among undated messages')
                elif ident in [4, 5]:
                    self.assertEqual(row['Selected User Message'], '')
                    self.assertEqual(row['Selection Basis'], 'no eligible message')
                else:
                    self.assertEqual(row['Selection Basis'], 'earliest recorded timestamp')
                if ident in [6, 7]:
                    self.assertEqual(row['Selected User Message'], '')
                    self.assertNotEqual(row['Selected User Message At'], '')
            self.assertEqual(len({row['Source File'] for row in rows}), 2)

    def test_no_database_returns_empty_without_error(self):
        headers, rows, sources = nova.nova_chatbot_history.__wrapped__(Context('.', []))
        self.assertEqual(rows, [])
        self.assertEqual(sources, '')
        self.assertEqual(headers[-1], 'Source File')
