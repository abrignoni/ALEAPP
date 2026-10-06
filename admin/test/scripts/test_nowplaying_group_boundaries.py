"""Real SQLite/protobuf histories preserve group starts and the legacy timestamp rule."""
import hashlib
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from scripts import blackboxprotobuf
from scripts.artifacts import googleNowPlaying as module


MISSING = object()
SQL = '''Select CASE timestamp WHEN "0" THEN "" ELSE datetime(timestamp / 1000, "unixepoch") END AS "timestamp", history_entry FROM recognition_history'''


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def protobuf(title, duration=60.0, artist='artist', album='album'):
    value = {'7': b'UTC', '9': {'3': title.encode(), '4': artist.encode(),
                              '13': album.encode(), '14': b'2024'}}
    nested = {k: {'type': 'bytes', 'name': ''} for k in ['3', '4', '13', '14']}
    if duration is not MISSING:
        value['9']['6'] = duration
        nested['6'] = {'type': 'double', 'name': ''}
    typedef = {'7': {'type': 'bytes', 'name': ''},
               '9': {'type': 'message', 'name': '', 'message_typedef': nested}}
    return blackboxprotobuf.encode_message(value, typedef)


def write_database(path, cases, wal=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    if wal:
        db.execute('pragma journal_mode=WAL')
        db.execute('pragma wal_autocheckpoint=0')
    db.execute('CREATE TABLE recognition_history(timestamp INTEGER,history_entry BLOB,unused TEXT)')
    db.commit()
    if wal:
        db.execute('pragma wal_checkpoint(TRUNCATE)')
    for timestamp, title, duration in cases:
        db.execute('insert into recognition_history values(?,?,?)',
                   (timestamp, protobuf(title, duration), 'not selected'))
    db.commit()
    return db


class NowPlayingGroupBoundariesTest(unittest.TestCase):
    def test_actual_protobuf_transitions_and_preescape_keys(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'com.google.android.as/databases/history_db'
            cases = [(1700000000000 + i * 1000, title, 60.0)
                     for i, title in enumerate(['A & <é>', 'A & <é>', 'B', 'B', 'C'])]
            db = write_database(path, cases)
            selected = db.execute(SQL).fetchall()
            db.close()
            decoded, _ = blackboxprotobuf.decode_message(selected[0][1])
            self.assertEqual(decoded['9']['3'], 'A & <é>'.encode())
            with patch.object(module, 'logfunc'):
                headers, rows, source = module.get_googleNowPlaying.__wrapped__(Context(folder, [path]))
            self.assertEqual(len(rows), 3)
            self.assertEqual([row[2] for row in rows], ['A &amp; &lt;é&gt;', 'B', 'C'])
            self.assertEqual([row[0] for row in rows],
                             [selected[0][0] + ',<br />' + selected[1][0],
                              selected[2][0] + ',<br />' + selected[3][0], selected[4][0]])
            self.assertEqual([row[4] for row in rows], ['00:01:00'] * 3)
            self.assertEqual(headers[0], 'Timestamp')
            self.assertEqual(source, str(path))

    def test_legacy_suppression_and_row_local_missing_duration(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'com.google.android.as/databases/history_db'
            cases = [(1700000000000, 'A', 60.0), (1700000000000, 'A', 60.0),
                     (1700000001000, 'A', 60.0), (1700000001000, 'A', 60.0),
                     (1700000002000, 'A', MISSING), (1700000003000, 'A', 0.0)]
            db = write_database(path, cases)
            selected = db.execute(SQL).fetchall()
            db.close()
            with patch.object(module, 'logfunc'):
                _, rows, _ = module.get_googleNowPlaying.__wrapped__(Context(folder, [path]))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0][0], ',<br />'.join([selected[0][0], selected[2][0], selected[3][0]]))
            self.assertEqual([row[4] for row in rows], ['00:01:00', ''])
            first_missing = Path(folder) / 'com.google.intelligence.sense/db/history_db'
            db = write_database(first_missing, [(1700000000000, 'first', MISSING)])
            db.close()
            with patch.object(module, 'logfunc'):
                _, rows, source = module.get_googleNowPlaying.__wrapped__(Context(folder, [first_missing, path]))
            self.assertEqual(rows[0][4], '')
            self.assertEqual(len(rows), 3)
            self.assertEqual(source, str(path))

    def test_actual_wal_rows_hashes_and_selection_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / 'writer/history_db'
            writer = write_database(path, [(1700000000000, 'A', 60.0),
                                           (1700000001000, 'B', 60.0)], wal=True)
            control = root / 'main-only'
            shutil.copy2(path, control)
            db = sqlite3.connect(f'file:{control}?mode=ro', uri=True)
            self.assertEqual(db.execute('select count(*) from recognition_history').fetchone()[0], 0)
            db.close()
            dest = root / 'com.google.android.as/databases'
            dest.mkdir(parents=True)
            for source in path.parent.iterdir():
                target = dest / source.name
                shutil.copy2(source, target)
                target.chmod(0o444)
            dest.chmod(0o555)
            hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.iterdir()}
            mirror = root / 'mirror/com.google.android.as/databases/history_db'
            mirror.parent.mkdir(parents=True)
            shutil.copy2(path, mirror)
            with patch.object(module, 'logfunc'):
                _, rows, source = module.get_googleNowPlaying.__wrapped__(
                    Context(root, [mirror, dest / 'history_db-wal', dest / 'history_db']))
            self.assertEqual(len(rows), 2)
            self.assertEqual([r[2] for r in rows], ['A', 'B'])
            self.assertEqual(source, str(dest / 'history_db'))
            self.assertEqual(hashes, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.iterdir()})
            writer.close()
            dest.chmod(0o755)


if __name__ == '__main__':
    unittest.main()
