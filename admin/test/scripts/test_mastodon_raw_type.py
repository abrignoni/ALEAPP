"""Actual SQLite type values survive Mastodon notification projection."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from scripts.artifacts import mastodon as module


class Context:
    def __init__(self, files):
        self.files = files

    def get_files_found(self):
        return self.files


def notification_query():
    tree = ast.parse(Path(module.__file__).read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == 'get_mastodon_notifications')
    return next(n.args[1].value for n in ast.walk(function)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == '_query')


def type_cases():
    return [None, 0, 1, 2, 3, 4, -1, 999, '0', '2', 'unknown', '', 0.5, b'0']


def write_database(path, wal=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    if wal:
        db.execute('pragma journal_mode=WAL')
        db.execute('pragma wal_autocheckpoint=0')
    db.execute('CREATE TABLE notifications_all(type, json TEXT, id)')
    db.commit()
    if wal:
        db.execute('pragma wal_checkpoint(TRUNCATE)')
    payload = json.dumps({'created_at': '2026-01-01T02:00:00+02:00', 'account': {'acct': 'é & <name>'},
                          'status': {'url': 'https://example.invalid/?a=1&b=2',
                                     'content': '<p>first &amp; <b>last</b></p>', 'visibility': 'opaque',
                                     'created_at': '2025-12-31T20:00:00-04:00'}}, ensure_ascii=False)
    rows = [(value, payload, i) for i, value in enumerate(type_cases())]
    rows += [rows[7], (None, '{}', None)]
    db.executemany('INSERT INTO notifications_all VALUES (?,?,?)', rows)
    db.commit()
    return db


class MastodonRawTypeTest(unittest.TestCase):
    def test_native_values_case_and_every_cell(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'account.db'
            db = write_database(path)
            selected = db.execute(notification_query()).fetchall()
            db.close()
            headers, rows, source = module.get_mastodon_notifications.__wrapped__(Context([path]))
            expected = [(datetime.fromisoformat(r[0]).astimezone(timezone.utc) if r[0] else '', r[1], r[2], r[8], r[3],
                         'first & last' if r[4] else r[4], r[5], datetime.fromisoformat(r[6]).astimezone(timezone.utc) if r[6] else '', r[7]) for r in selected]
            self.assertEqual(rows, expected)
            self.assertEqual(len(rows), 16)
            self.assertEqual([row[3] for row in rows[:14]], type_cases())
            self.assertEqual([type(row[3]) for row in rows[:14]], [type(v) for v in type_cases()])
            self.assertEqual([row[2] for row in rows[:14]],
                             [None, 'Follow', None, 'Mention', 'Boost', 'Favorite', None,
                              None, None, None, None, None, None, None])
            self.assertEqual(rows[7], rows[14])
            self.assertEqual(rows[0][0], rows[0][7])
            self.assertEqual(rows[0][5], 'first & last')
            self.assertEqual(headers[2:4], ('Notification Type Interpretation', 'Type (As Stored)'))
            self.assertEqual(source, str(path))

    def test_target_integer_affinity_schema(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'account.db'
            db = sqlite3.connect(path)
            db.execute('CREATE TABLE notifications_all(id VARCHAR(25) NOT NULL PRIMARY KEY, '
                       'json TEXT NOT NULL, flags INTEGER NOT NULL DEFAULT 0, '
                       'type INTEGER NOT NULL, time INTEGER NOT NULL)')
            values = [0, 2, 3, 4, -1, 999, '0', 'unknown']
            db.executemany('INSERT INTO notifications_all(id,json,type,time) VALUES (?,?,?,?)',
                           [(str(i), '{}', value, 0) for i, value in enumerate(values)])
            db.commit()
            expected = db.execute('select type from notifications_all').fetchall()
            db.close()
            _, rows, _ = module.get_mastodon_notifications.__wrapped__(Context([path]))
            self.assertEqual([row[3] for row in rows], [row[0] for row in expected])
            self.assertEqual([type(row[3]) for row in rows], [type(row[0]) for row in expected])
            self.assertEqual(len(rows), len(values))

    def test_actual_wal_first_main_and_protected_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / 'writer/account.db'
            writer = write_database(path, wal=True)
            control = root / 'main-only.db'
            shutil.copy2(path, control)
            db = sqlite3.connect(f'file:{control}?mode=ro', uri=True)
            self.assertEqual(db.execute('select count(*) from notifications_all').fetchone()[0], 0)
            db.close()
            target = root / 'protected'
            target.mkdir()
            for p in path.parent.iterdir():
                shutil.copy2(p, target / p.name)
                (target / p.name).chmod(0o444)
            target.chmod(0o555)
            other = root / 'other.db'
            connection = write_database(other)
            connection.close()
            hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir()}
            _, rows, source = module.get_mastodon_notifications.__wrapped__(
                Context([target / 'account.db-wal', target / 'account.db', other]))
            self.assertEqual(len(rows), 16)
            self.assertEqual(source, str(target / 'account.db'))
            self.assertEqual(hashes, {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in target.iterdir()})
            writer.close()
            target.chmod(0o755)


if __name__ == '__main__':
    unittest.main()
