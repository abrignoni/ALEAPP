"""Read-only ATTACH tests.

Artifacts that need a second database open it with ATTACH DATABASE. When the
statement is built by pasting the filesystem path into SQL, SQLite opens that
database read-write even though the primary connection came from
open_sqlite_db_readonly - the attached evidence copy can then be written to,
and its -wal/-shm/journal siblings created, modified or checkpointed away.
ilapfuncs.attach_sqlite_db_readonly builds the same statement with a
"file:<path>?mode=ro" URI instead, which SQLite refuses to write to.

These tests pin both halves: no artifact hand-builds an ATTACH statement, and
the helper's statement really does produce a read-only attachment.
"""
import os
import re
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.ilapfuncs import attach_sqlite_db_readonly, open_sqlite_db_readonly

ARTIFACTS_DIR = Path(ROOT_DIR, 'scripts', 'artifacts')

# Matches an ATTACH statement written out in artifact source, however the path
# is interpolated (concatenation, %-format or f-string).
ATTACH_LITERAL = re.compile(r'attach\s+database', re.IGNORECASE)


class TestArtifactsUseReadonlyAttach(unittest.TestCase):
    def test_no_artifact_builds_its_own_attach_statement(self):
        offenders = []
        for py_file in sorted(ARTIFACTS_DIR.glob('*.py')):
            source = py_file.read_text(encoding='utf-8')
            for lineno, line in enumerate(source.splitlines(), start=1):
                if ATTACH_LITERAL.search(line):
                    offenders.append(f'{py_file.name}:{lineno}: {line.strip()}')

        self.assertEqual(
            offenders, [],
            'Artifacts must attach a second database with '
            'ilapfuncs.attach_sqlite_db_readonly() so the evidence copy is '
            'opened read-only. Hand-built statements found:\n' + '\n'.join(offenders))


class TestAttachSqliteDbReadonly(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix='aleapp_attach_ro_'))
        self.addCleanup(self._cleanup)

        self.main_db = self.test_dir / 'main.db'
        self.attached_db = self.test_dir / 'attached.db'
        for db_path, table in ((self.main_db, 'main_rows'), (self.attached_db, 'attached_rows')):
            connection = sqlite3.connect(db_path)
            connection.execute(f'CREATE TABLE {table} (value TEXT)')
            connection.execute(f"INSERT INTO {table} VALUES ('expected')")
            connection.commit()
            connection.close()

    def _cleanup(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_attached_database_is_readable(self):
        db = open_sqlite_db_readonly(str(self.main_db))
        self.addCleanup(db.close)
        cursor = db.cursor()
        cursor.execute(attach_sqlite_db_readonly(str(self.attached_db), 'attached'))
        self.assertEqual(
            cursor.execute(
                'SELECT main_rows.value, attached.attached_rows.value '
                'FROM main_rows, attached.attached_rows').fetchone(),
            ('expected', 'expected'),
        )

    def test_attached_database_rejects_writes(self):
        db = open_sqlite_db_readonly(str(self.main_db))
        self.addCleanup(db.close)
        cursor = db.cursor()
        cursor.execute(attach_sqlite_db_readonly(str(self.attached_db), 'attached'))
        with self.assertRaises(sqlite3.OperationalError) as raised:
            cursor.execute('CREATE TABLE attached.write_probe (value TEXT)')
        self.assertIn('readonly', str(raised.exception))


if __name__ == '__main__':
    unittest.main()
