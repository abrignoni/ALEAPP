"""Cookie filename case and thumbnails without a usable filename timestamp."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from scripts.artifacts import DuckDuckGo as artifact

PACKAGE = 'com.duckduckgo.mobile.android'
FILENAMES = ('1700000000000.jpg', 'not-a-time.jpg', '9'*100 + '.jpg')


def create_fixture(root):
    root = Path(root)
    app = root / 'CONSTRUCTED/data/data' / PACKAGE
    files = []
    for parent, name, host in [(app, 'Cookies', 'upper.example'),
                               (root/'CONSTRUCTED/data/user/10'/PACKAGE, 'cookies', 'lower.example')]:
        path = parent / 'app_webview/Default' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(path)
        db.execute('CREATE TABLE cookies (last_access_utc,host_key,name,value,creation_utc,expires_utc,path)')
        db.execute('INSERT INTO cookies VALUES (?,?,?,?,?,?,?)',
                   (13344473600000000, host, 'session', '<escaped & value>', 0, 0, '/'))
        db.commit()
        db.close()
        files.append(path)
        sidecar = path.with_name(path.name+'-journal')
        sidecar.write_bytes(b'')
        files.append(sidecar)
    path = app/'databases/app.db'
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE tabs (tabPreviewFile)')
    db.execute('INSERT INTO tabs VALUES (?)', (FILENAMES[0],))
    db.commit()
    db.close()
    files.append(path)
    for name in FILENAMES:
        path = app/'cache/tabPreviews/session'/name
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new('RGB', (4, 4), 'blue').save(path, format='JPEG')
        files.append(path)
    return files


class Context:
    def __init__(self, root, files):
        self.root, self.files = Path(root), files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def reader(source, query):
    connection = sqlite3.connect(source)
    try:
        return connection.execute(query).fetchall()
    finally:
        connection.close()


class TestDuckDuckGoEdges(unittest.TestCase):
    def test_both_cookie_cases_and_main_file_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_fixture(directory)
            files = [p for p in files if p.name.startswith(('Cookies', 'cookies'))]
            with patch.object(artifact, 'get_sqlite_db_records', side_effect=reader):
                headers, rows, source = artifact.duckduckgo_cookies.__wrapped__(Context(directory, files))
        self.assertEqual([h[0] for h in headers[:3]], ['Last Accessed', 'Creation Time', 'Expiry'])
        self.assertEqual(len(rows), 2)
        self.assertCountEqual([r[3] for r in rows], ['upper.example', 'lower.example'])
        self.assertTrue(all(r[5] == '<escaped & value>' for r in rows))
        self.assertTrue(all(not Path(r[-1]).is_absolute() for r in rows))
        self.assertTrue(all('-journal' not in r[-1] for r in rows))
        self.assertEqual(set(source.splitlines()), {r[-1] for r in rows})

    def test_mixed_names_preserve_images_with_blank_unknown_times(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_fixture(directory)
            files = [p for p in files if p.suffix == '.jpg' or p.name == 'app.db']
            with patch.object(artifact, 'get_sqlite_db_records', side_effect=reader), \
                 patch.object(artifact, 'check_in_media', side_effect=lambda p, _: 'media:'+Path(p).name), \
                 patch.object(artifact, 'logfunc') as log:
                headers, rows, _ = artifact.duckduckgo_thumbnails.__wrapped__(Context(directory, files))
        self.assertEqual(headers[0], ('Timestamp (UTC)', 'datetime'))
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0][0], '2023-11-14 22:13:20')
        self.assertEqual(rows[0][1], 'Yes')
        self.assertEqual([r[0] for r in rows[1:]], [None, None])
        self.assertEqual([r[3] for r in rows], list(FILENAMES))
        self.assertTrue(all(r[2] and r[4].endswith(r[3]) for r in rows))
        self.assertEqual(log.call_count, 2)

    def test_thumbnail_only_input_never_queries_an_image(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'not-a-time.jpg'
            path.write_bytes(b'fixture')
            with patch.object(artifact, 'get_sqlite_db_records') as query, \
                 patch.object(artifact, 'check_in_media', return_value='media'), \
                 patch.object(artifact, 'logfunc'):
                _, rows, _ = artifact.duckduckgo_thumbnails.__wrapped__(Context(directory, [path]))
            query.assert_not_called()
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0][0])


if __name__ == '__main__':
    unittest.main()
