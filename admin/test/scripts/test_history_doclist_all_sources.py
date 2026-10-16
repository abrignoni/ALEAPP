"""Distinct source survival, repeated histories and explicit empty/error distinctions."""
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scripts.artifacts import BashHistory as history
from scripts.artifacts import DocList as documents

FIELDS = ('creationTime', 'title', 'owner', 'lastModifiedTime', 'lastOpenedTime',
          'lastModifierAccountAlias', 'lastModifierAccountName', 'kind', 'shareableUri',
          'htmlUri', 'md5Checksum', 'size')
MISSING = ('owner', 'lastModifierAccountAlias', 'lastModifierAccountName', 'shareableUri')


def create_fixture(root, include_bad=True):
    root = Path(root)
    files = []
    for user, commands in [('data/data', 'same\nsame\nother\n'),
                            ('data/user/10', 'other\nsame\n')]:
        path = root/'CONSTRUCTED'/user/'com.termux/files/home/.bash_history'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(commands, encoding='utf-8')
        files.append(path)
    alias = root/'CONSTRUCTED/data/user/0/com.termux/files/home/.bash_history'
    alias.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(files[0], alias)
    files.append(alias)
    for user, title, missing in [(0, 'first <document>', False), (10, 'second', False),
                                 (11, 'schema variant', True), (12, None, False),
                                 (13, 'BAD', False)]:
        if title == 'BAD' and not include_bad:
            continue
        path = root/f'CONSTRUCTED/data/user/{user}/com.google.android.apps.docs/databases/DocList.db'
        path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(path)
        if title != 'BAD':
            fields = [field for field in FIELDS if not missing or field not in MISSING]
            db.execute(f'CREATE TABLE EntryView ({",".join(fields)})')
            if title is not None:
                values = dict(zip(FIELDS, (1700000000000, title, 'owner', 1700000001000,
                                          None, 'alias', 'name', 'file', 'share', 'html', 'md5', 5)))
                db.execute(f'INSERT INTO EntryView VALUES ({",".join("?" for _ in fields)})',
                           [values[field] for field in fields])
        else:
            db.execute('CREATE TABLE unrelated (value)')
        db.commit()
        db.close()
        sidecar = path.with_name(path.name+'-journal')
        sidecar.write_bytes(b'')
        files.extend([sidecar, path])
    return files


class Context:
    def __init__(self, root, files):
        self.root, self.files = Path(root), files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


class TestHistoryDocListSources(unittest.TestCase):
    def test_histories_preserve_repeated_lines_and_distinct_users(self):
        with tempfile.TemporaryDirectory() as directory:
            files = [p for p in create_fixture(directory) if p.name == '.bash_history']
            _, rows, sources = history.bashHistory.__wrapped__(Context(directory, files))
        self.assertEqual([r[:2] for r in rows], [(1, 'same\n'), (2, 'same\n'), (3, 'other\n'),
                                               (1, 'other\n'), (2, 'same\n')])
        self.assertEqual(len(sources.splitlines()), 2)
        self.assertTrue(all(not Path(r[2]).is_absolute() for r in rows))

    def test_documents_keep_other_sources_and_log_bad_not_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            files = [p for p in create_fixture(directory) if p.name != '.bash_history']
            with patch.object(documents, 'logfunc') as log:
                headers, rows, sources = documents.get_DocList.__wrapped__(Context(directory, files))
            # The schema helper logs missing columns separately; query errors go through this module.
            errors = [call.args[0] for call in log.call_args_list]
        self.assertEqual([h[0] for h in headers[:3]], ['Created Date', 'Modified Date', 'Opened Date'])
        self.assertEqual([r[3] for r in rows], ['first <document>', 'second', 'schema variant'])
        self.assertIsNone(rows[2][4])
        self.assertIsNone(rows[2][8])
        self.assertTrue(all(r[2] is None for r in rows))
        self.assertEqual(len(sources.splitlines()), 5)
        self.assertEqual(len(errors), 1)
        self.assertIn('data/user/13', errors[0])
        self.assertIn('no such table: EntryView', errors[0])
        self.assertNotIn('data/user/12', errors[0])
        self.assertTrue(all('-journal' not in r[-1] for r in rows))


if __name__ == '__main__':
    unittest.main()
