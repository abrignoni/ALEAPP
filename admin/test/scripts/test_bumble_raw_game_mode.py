"""Raw SQLite values, duplicate occurrences and complete WAL selection."""
from pathlib import Path
import hashlib
import shutil
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts import bumble as artifact  # pylint: disable=wrong-import-position


class Context:
    def __init__(self, root, files):
        self.root, self.files = Path(root), files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in Path(root).rglob('*') if p.is_file()}


def create_store(root, tenant='', wal=False, prefix=''):
    folder = Path(root) / tenant / 'data/data/com.bumble.app/databases'
    folder.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as work:
        source = Path(work) / 'ChatComDatabase'
        connection = sqlite3.connect(source)
        if wal:
            connection.execute('pragma journal_mode=wal')
            connection.execute('pragma wal_autocheckpoint=0')
        connection.execute('CREATE TABLE conversation_info(user_name,age,gender,game_mode,user_image_url,user_id,encrypted_user_id)')
        connection.commit()
        if wal:
            connection.execute('pragma wal_checkpoint(truncate)')
        values = [None, 0, 1, 5, 2, -1, 0.0, 1.0, 5.0, 1.25, '0', '1', 'BumbleDate', '', b'\x00\xff']
        rows = [(prefix + 'record-' + str(i), 20 + i, 'stored-gender', v, 'https://example.invalid/' + str(i), i, 'encrypted-' + str(i)) for i, v in enumerate(values)]
        rows.extend([rows[2], ('tie', 33, None, -8, None, 2, None)])
        connection.executemany('INSERT INTO conversation_info VALUES(?,?,?,?,?,?,?)', rows)
        connection.commit()
        # Each immutable copied state gets only its own main and sidecars.
        for item in Path(work).glob('ChatComDatabase*'):
            target = folder / item.name
            shutil.copyfile(item, target)
            assert hashlib.sha256(item.read_bytes()).digest() == hashlib.sha256(target.read_bytes()).digest()
            target.chmod(0o444)
        connection.close()
    return folder / 'ChatComDatabase'


def direct_rows(path):
    connection = sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True)
    assert connection.execute('pragma integrity_check').fetchall() == [('ok',)]
    assert connection.execute('pragma quick_check').fetchall() == [('ok',)]
    rows = connection.execute('SELECT user_name,age,gender,game_mode,user_image_url,user_id,encrypted_user_id FROM conversation_info ORDER BY user_id').fetchall()
    types = connection.execute('SELECT typeof(game_mode),hex(game_mode) FROM conversation_info ORDER BY user_id').fetchall()
    connection.close()
    return rows, types


class TestRawGameMode(unittest.TestCase):
    def check_store(self, root, path, files):
        initial = hashes(root)
        headers, rows, source = artifact.get_bumble_matches.__wrapped__(Context(root, files))
        oracle, types = direct_rows(path)
        self.assertEqual(rows, oracle)
        self.assertEqual(len(rows), 17)
        self.assertEqual(len(headers), 7)
        self.assertEqual(headers[3], 'game_mode (as stored)')
        self.assertEqual(source, str(path))
        for actual, expected in zip(rows, oracle):
            self.assertEqual([type(v) for v in actual], [type(v) for v in expected])
        self.assertEqual(rows.count(rows[2]), 2)
        self.assertEqual(set(t[0] for t in types), {'null', 'integer', 'real', 'text', 'blob'})
        self.assertEqual(hashes(root), initial)

    def test_native_types_and_duplicate_occurrences(self):
        with tempfile.TemporaryDirectory() as root:
            path = create_store(root)
            self.check_store(root, path, [path])

    def test_uncheckpointed_wal_and_main_only_control(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as control:
            path = create_store(root, wal=True)
            self.assertGreater(Path(str(path) + '-wal').stat().st_size, 0)
            self.check_store(root, path, [path])
            target = Path(control) / 'ChatComDatabase'
            shutil.copyfile(path, target)
            target.chmod(0o444)
            self.assertEqual(direct_rows(target)[0], [])

    def test_first_main_sidecars_and_empty_selection(self):
        with tempfile.TemporaryDirectory() as root:
            a = create_store(root, 'a', wal=True, prefix='A')
            b = create_store(root, 'b', wal=True, prefix='B')
            self.check_store(root, b, [Path(str(a) + '-wal'), Path(str(b) + '-shm'), b, a])
            headers, rows, source = artifact.get_bumble_matches.__wrapped__(Context(root, [Path(str(a) + '-wal')]))
            self.assertEqual((len(headers), rows, source), (7, [], ''))


if __name__ == '__main__':
    unittest.main()
