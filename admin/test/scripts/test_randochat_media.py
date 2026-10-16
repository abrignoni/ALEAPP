"""Empty and substring-only stored filenames cannot attach unrelated media."""
import base64
import pathlib
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.RandoChat import randochat_messages

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')
URLS = [None, '', 'https://host/', 'missing.png', 'https://host/exact.png', 'part.png', 'https://host/exact.png', 'https://host/quote"<&.png']

def make_fixture(root):
    root = pathlib.Path(root)
    db = root / 'data/data/com.random.chat.app/databases/ramdochatV2.db'
    db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db)
    con.execute('CREATE TABLE mensagens(hora,mensagem,minha,url,id_talk_server,id_servidor)')
    con.execute('CREATE TABLE conversa(id_server,apelido)')
    con.execute('INSERT INTO conversa VALUES(1,\'Contact\')')
    for index, url in enumerate(URLS):
        con.execute('INSERT INTO mensagens VALUES(?,?,?,?,?,?)', (1700000000000, 'Content', 2, url, 1, index))
    con.commit()
    con.close()
    paths = [db]
    for name in ['exact.png', 'part.png-extra.png', 'quote"<&.png']:
        target = root / 'data/media/0/Android/data/com.random.chat.app/files/images' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(PNG)
        paths.append(target)
    return paths

class RandoChatMediaTest(unittest.TestCase):
    def test_exact_nonempty_matching_and_stored_url(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = make_fixture(folder)
            with patch('scripts.artifacts.RandoChat.check_in_media', side_effect=lambda path, name: name) as media:
                headers, rows, source = randochat_messages.__wrapped__(context(folder, paths))
            self.assertEqual(len(rows), len(URLS))
            self.assertEqual([row[headers.index('Stored Media URL')] for row in rows], URLS)
            self.assertEqual([row[headers.index(('Media File', 'media'))] for row in rows], [0, '', '', '', 'exact.png', '', 'exact.png', 'quote"<&.png'])
            self.assertEqual(media.call_count, 3)
            self.assertTrue(all(pathlib.Path(call.args[0]).name in ['exact.png', 'quote"<&.png'] for call in media.call_args_list))
            self.assertEqual(source, str(paths[0]))
            self.assertNotIn('Source File', headers)
            self.assertEqual(rows[4][:-1], rows[6][:-1])
