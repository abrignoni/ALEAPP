"""SQLite storage classes, join multiplicity and live WAL for MX Player Read."""
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import mxPlayer


class TestMxPlayerRawRead(unittest.TestCase):
    def context(self, root, paths):
        return SimpleNamespace(get_files_found=lambda: paths,
                               get_relative_path=lambda p: str(Path(p).relative_to(root)))

    def schema(self, db, affinity=''):
        db.execute('CREATE TABLE VideoFile(LastWatchTime,FinishTime,LastModified,FileName,Directory,Duration,Size,Width,Height,VideoTrackCount,AudioTrackCount,SubtitleTrackCount,Read ' + affinity + ',Id)')
        db.execute('CREATE TABLE VideoDirectory(Id,Path)')
        db.execute('CREATE TABLE VideoStates(Uri,Position,DecodeMode,PlaybackSpeed)')
        db.execute('INSERT INTO VideoDirectory VALUES(1,"/Movies/Known Folder")')
        db.execute('INSERT INTO VideoStates VALUES("file:///Movies/Known%20Folder/clip.mp4/",0,"native",0)')

    def insert(self, db, value, identity):
        db.execute('INSERT INTO VideoFile VALUES(1700000000000,0,1700000100000,"clip.mp4",1,15000,8,1920,1080,1,1,0,?,?)', (value, identity))

    def test_actual_read_affinities_and_storage_classes(self):
        values = [None, 0, 1, -1, 0.0, 0.5, '0', '1', '', 'unknown', b'', b'0']
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for affinity in ['', 'TEXT', 'INTEGER']:
                with self.subTest(affinity=affinity):
                    path = root / (affinity or 'NONE') / 'databases/medias.db'
                    path.parent.mkdir(parents=True)
                    db = sqlite3.connect(path)
                    self.schema(db, affinity)
                    for identity, value in enumerate(values):
                        self.insert(db, value, identity)
                    db.commit()
                    stored = db.execute('SELECT Read FROM VideoFile ORDER BY LastWatchTime DESC,Id').fetchall()
                    db.close()
                    headers, rows, source = mxPlayer.mxplayer_media_library.__wrapped__(self.context(root, [str(path)]))
                    self.assertEqual(len(headers), 14)
                    self.assertEqual(headers[11], 'Read (As Stored)')
                    self.assertEqual([(r[11], type(r[11])) for r in rows], [(r[0], type(r[0])) for r in stored])
                    self.assertIsNone(rows[0][11])
                    self.assertEqual(rows[9][11], 'unknown')
                    self.assertEqual(rows[10][11], b'')
                    self.assertEqual(source, str(path))

    def test_schema_wal_alias_join_and_watched_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'data/user/0/com.mxtech.videoplayer.ad/databases/medias.db'
            path.parent.mkdir(parents=True)
            db = sqlite3.connect(path)
            try:
                db.execute('CREATE TABLE unrelated(x)')
                db.commit()
                db.execute('PRAGMA journal_mode=WAL')
                db.execute('PRAGMA wal_autocheckpoint=0')
                self.schema(db)
                db.execute('INSERT INTO VideoDirectory SELECT * FROM VideoDirectory')
                self.insert(db, None, 1)
                self.insert(db, '0', 2)
                db.commit()
                alias = root / 'data/data/com.mxtech.videoplayer.ad/databases/medias.db'
                alias.parent.mkdir(parents=True)
                for suffix in ['', '-wal', '-shm']:
                    shutil.copy2(str(path) + suffix, str(alias) + suffix)
                context = self.context(root, [str(path), str(alias)])
                _, rows, source = mxPlayer.mxplayer_media_library.__wrapped__(context)
                self.assertEqual([r[11] for r in rows], [None, None, '0', '0'])
                self.assertEqual(source, str(alias))
                headers, watched, watched_source = mxPlayer.mxplayer_watched.__wrapped__(context)
                self.assertEqual(len(headers), 12)
                self.assertEqual(len(watched), 4)
                self.assertEqual([(r[5], r[7], r[8]) for r in watched], [(0, 'native', 0)] * 4)
                self.assertEqual(watched_source, source)
            finally:
                db.close()


if __name__ == '__main__':
    unittest.main()
