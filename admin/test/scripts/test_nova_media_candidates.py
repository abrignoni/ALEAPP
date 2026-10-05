"""Filename collisions preserve candidates, user scopes and physical evidence."""
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
from scripts.artifacts import AIChatbotNovaConversations as conversations
from scripts.artifacts import AIChatbotNovaMediastore as media


def create_fixture(root):
    root = Path(root)
    for prefix, label in [('data/data', 'zero'), ('data/user/10', 'ten'), ('misc', 'unknown')]:
        path = root/prefix/'com.scaleup.chatai/databases/chat-ai.db'
        path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(path)
        db.execute('CREATE TABLE History (id,UUID,title,chatBotModel,assistantId,softDeleted,syncState)')
        db.execute('CREATE TABLE HistoryDetail (id,UUID,historyID,type,text,token,reasoningContent,createdAt,syncState)')
        db.execute('CREATE TABLE HistoryDetailImage (historyDetailID,url,prompt)')
        db.execute('CREATE TABLE HistoryDetailDocument (historyDetailID,name,mimeType,url)')
        db.execute('CREATE TABLE HistoryDetailLink (historyDetailID,url)')
        db.execute('INSERT INTO History VALUES (1,?,?,?,?,?,?)',
                   ('conversation', f'{label} <conversation>', 0, 1, 0, 0))
        db.executemany('INSERT INTO HistoryDetail VALUES (?,?,?,?,?,?,?,?,?)',
                       [(1, 'doc', 1, None if label == 'unknown' else 0, label+' document',
                         1, '', 1700000000000, 0),
                        (2, 'image', 1, 1, label+' image', 1, '', 1700000001000, 0)])
        db.execute('INSERT INTO HistoryDetailDocument VALUES (1,?,?,?)',
                   ('same.txt', 'text/plain', 'https://example.test/same.txt'))
        db.execute('INSERT INTO HistoryDetailImage VALUES (2,?,?)',
                   ('https://example.test/same.jpg', '<prompt>'))
        db.commit()
        db.close()
    for prefix, user in [('data/data', '0'), ('data/user/10', '10'), ('misc', 'unknown')]:
        path = root/prefix/'com.google.android.providers.media.module/databases/external.db'
        path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(path)
        db.execute('CREATE TABLE files (_display_name,_data)')
        db.executemany('INSERT INTO files VALUES (?,?)',
                       [('same.jpg', f'/storage/emulated/{user}/first/same.jpg'),
                        ('same.JPG', f'/storage/emulated/{user}/second/same.jpg'),
                        ('same.txt', f'/storage/emulated/{user}/same.txt')])
        db.commit()
        db.close()
    for package, name in [('com.scaleup.chatai', 'chat-ai.db'),
                          ('com.google.android.providers.media.module', 'external.db')]:
        original = root/'data/data'/package/'databases'/name
        for prefix in ['data/user/0', 'data_mirror/data_ce/null/0']:
            target = root/prefix/package/'databases'/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original, target)
    for user, folder, filename, color in [('0','first','same.jpg','red'),
                                          ('0','second','same.jpg','blue'),
                                          ('10','first','same.jpg','green'),
                                          ('unknown','first','same.jpg','yellow'),
                                          ('0','first','orphan.jpg','purple')]:
        path = root/f'data/media/{user}/Android/media/com.scaleup.chatai/Nova/{folder}/{filename}'
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new('RGB', (3, 3), color).save(path)
    for user in ['0', '10']:
        path = root/f'data/media/{user}/Android/media/com.scaleup.chatai/Nova/same.txt'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('document '+user)
    return sorted(path for path in root.rglob('*') if path.is_file())


class Context:
    def __init__(self, root, files):
        self.root, self.files = Path(root), files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def named_rows(headers, rows):
    names = [header[0] if isinstance(header, tuple) else header for header in headers]
    return [dict(zip(names, row)) for row in rows]


class TestNovaMediaCandidates(unittest.TestCase):
    def test_conversations_keep_candidates_and_unknown_scope(self):
        with tempfile.TemporaryDirectory() as root:
            files = create_fixture(root)
            with patch.object(conversations, 'check_in_media', return_value='candidate'):
                headers, rows, sources = conversations.nova_chatbot_conversations.__wrapped__(
                    Context(root, files))
                _, reversed_rows, _ = conversations.nova_chatbot_conversations.__wrapped__(
                    Context(root, list(reversed(files))))
            self.assertEqual(rows, reversed_rows)
            self.assertEqual(len(rows), 6)
            self.assertEqual(headers[0], ('Message Timestamp (UTC)', 'datetime'))
            records = named_rows(headers, rows)
            self.assertEqual(len({row['Source File'] for row in records}), 3)
            images = [row for row in records if row['Image Cloud URL']]
            self.assertTrue(all(not row['Image Media Candidate'] for row in images))
            self.assertTrue(all('unknown' in row['Image Filesystem Match Scope'] for row in images))
            self.assertTrue(all(len(row['Image MediaStore Candidate Sources'].splitlines()) == 6
                                for row in images))
            known_docs = [row for row in records if row['Document Name']
                          and not row['Source File'].startswith('misc/')]
            self.assertTrue(all(row['Document Media Candidate'] for row in known_docs))
            self.assertTrue(all('data/media/' in row['Document Media Candidate Source']
                                for row in known_docs))
            unknown = next(row for row in records if row['Source File'].startswith('misc/'))
            self.assertIn('unknown', unknown['Document MediaStore Match Scope'])
            self.assertFalse(unknown['Document Media Candidate'])
            self.assertTrue(all(not Path(source).is_absolute() for source in sources.splitlines()))

    def test_unique_known_user_file_is_only_a_scoped_candidate(self):
        with tempfile.TemporaryDirectory() as root:
            files = [path for path in create_fixture(root)
                     if '/data/media/unknown/' not in str(path)]
            with patch.object(conversations, 'check_in_media', return_value='candidate'):
                headers, rows, _ = conversations.nova_chatbot_conversations.__wrapped__(
                    Context(root, files))
            images = [row for row in named_rows(headers, rows) if row['Image Cloud URL']]
            ten = next(row for row in images if '/user/10/' in row['Source File'])
            self.assertEqual(ten['Image Media Candidate'], 'candidate')
            self.assertTrue(ten['Image Media Candidate Source'].startswith('data/media/10/'))
            zero = next(row for row in images if row['Source File'].startswith('data/data/'))
            self.assertFalse(zero['Image Media Candidate'])
            self.assertIn('2 same scope', zero['Image Filesystem Match Scope'])

    def test_media_retains_sides_and_ambiguous_physical_files(self):
        with tempfile.TemporaryDirectory() as root:
            files = create_fixture(root)
            files += [path for path in Path(root).rglob('*') if path.is_dir()]
            with patch.object(media, 'check_in_media', return_value='candidate') as export:
                headers, rows, _ = media.nova_user_submissions.__wrapped__(Context(root, files))
            records = named_rows(headers, rows)
            self.assertEqual(headers[0], ('Date', 'datetime'))
            self.assertEqual(len(records), 11)  # Six DB records and five ambiguous/orphan files.
            db_rows = [row for row in records if row['Type'] != 'Filesystem Media']
            self.assertEqual({row['Message Type'] for row in db_rows}, {None, 0, 1})
            self.assertEqual(len({row['Source File'] for row in db_rows}), 3)
            physical = [row for row in records if row['Type'] == 'Filesystem Media']
            self.assertEqual(len(physical), 5)
            self.assertEqual(len({row['Source File'] for row in physical}), 5)
            exported_paths = {call.args[0] for call in export.call_args_list}
            self.assertEqual(len(exported_paths), 7)
            self.assertTrue(all(Path(path).is_file() for path in exported_paths))
            self.assertEqual(media.__artifacts_v2__['nova_user_submissions']['name'], 'Nova Media Records')


if __name__ == '__main__':
    unittest.main()
