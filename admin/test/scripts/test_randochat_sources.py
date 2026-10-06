"""Each SQLite state keeps local joins, settings and row origins."""
import pathlib
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from admin.test.scripts.test_randochat_media import PNG
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.RandoChat import randochat_messages, randochat_account, randochat_contacts, open_sqlite_db_readonly

PARSERS = [randochat_messages, randochat_account, randochat_contacts]

def make_database(path, label='first', empty=False, bad=False):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    if bad:
        con.execute('CREATE TABLE unrelated(value)')
    else:
        con.execute('CREATE TABLE mensagens(hora,mensagem,minha,url,id_talk_server,id_servidor)')
        con.execute('CREATE TABLE conversa(id_server,id_pessoa,apelido,idade,sexo,favorite,bloqueado,images)')
        con.execute('CREATE TABLE configuracao(name,value)')
        if not empty:
            con.executemany('INSERT INTO mensagens VALUES(1700000000000,?,2,\'unique.png\',1,1)', [(label,)] * 2)
            con.executemany('INSERT INTO conversa VALUES(?,1,?,20,\'X\',1,0,\'\')', [(1, label), (2, label)])
            con.executemany('INSERT INTO configuracao VALUES(?,?)', [('apelido', label), ('sexo', 'X'), ('sexo_search', 'M')])
    con.commit()
    con.close()
    return path

def make_multisource(root):
    root = pathlib.Path(root)
    first = make_database(root / 'data/data/com.random.chat.app/databases/ramdochatV2.db')
    alias = root / 'data/user/0/com.random.chat.app/databases/ramdochatV2.db'
    alias.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(first, alias)
    second = make_database(root / 'data/user/10/com.random.chat.app/databases/ramdochatV2.db', 'user10')
    third = make_database(root / 'OtherRoot/data/data/com.random.chat.app/databases/ramdochatV2.db', 'prefix')
    bad = make_database(root / 'data/user/20/com.random.chat.app/databases/ramdochatV2.db', bad=True)
    media = root / 'data/media/0/Android/data/com.random.chat.app/files/images/unique.png'
    media.parent.mkdir(parents=True, exist_ok=True)
    media.write_bytes(PNG)
    wrong = make_database(root / 'data/data/com.random.chat.app/databases/ramdochatV2.db-backup', 'wrong-basename')
    make_database(root / 'data/data/com.unrelated.app/databases/ramdochatV2.db', 'wrong-package')
    return [bad, first, alias, second, third, media, wrong]

class RandoChatSourcesTest(unittest.TestCase):
    def test_distinct_sources_local_join_max_and_duplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = make_multisource(folder)
            for parser, count in zip(PARSERS, [6, 3, 6]):
                with patch('scripts.artifacts.RandoChat.check_in_media', return_value='ref'), patch('scripts.artifacts.RandoChat.logfunc') as log:
                    headers, rows, sources = parser.__wrapped__(context(folder, paths))
                self.assertEqual(len(rows), count)
                self.assertEqual(headers[-1], 'Source File')
                self.assertEqual(len(sources.splitlines()), 3)
                for row in rows:
                    label = 'user10' if '/10/' in row[-1] else 'prefix' if row[-1].startswith('OtherRoot') else 'first'
                    self.assertEqual(row[headers.index('Contact Username' if parser is randochat_messages else 'Username')], label)
                    if parser is randochat_messages:
                        self.assertEqual(row[headers.index('Content')], label)
                        self.assertEqual(row[headers.index('Media Filename Candidate Count')], 1)
                self.assertTrue(any('unsupported' in call.args[0] and '20' in call.args[0] for call in log.call_args_list))

    def test_actual_wal_conflicting_states(self):
        with tempfile.TemporaryDirectory() as folder:
            live = make_database(pathlib.Path(folder) / 'live', empty=True)
            con = sqlite3.connect(live)
            con.execute('PRAGMA journal_mode=WAL')
            con.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            paths = []
            for user, label in [('data/data', 'one'), ('data/user/0', 'two')]:
                con.execute('INSERT INTO mensagens VALUES(1700000000000,?,2,NULL,1,1)', (label,))
                con.execute('INSERT INTO conversa VALUES(1,1,?,20,\'X\',1,0,\'\')', (label,))
                con.execute('INSERT INTO configuracao VALUES(\'apelido\',?)', (label,))
                con.commit()
                target = pathlib.Path(folder) / user / 'com.random.chat.app/databases/ramdochatV2.db'
                target.parent.mkdir(parents=True, exist_ok=True)
                for suffix in ['', '-wal', '-shm']:
                    shutil.copy2(str(live) + suffix, str(target) + suffix)
                paths.append(target)
            con.close()
            self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())
            for parser, count in zip(PARSERS, [5, 2, 3]):
                headers, rows, sources = parser.__wrapped__(context(folder, paths))
                self.assertEqual(len(rows), count)
                self.assertEqual(len(sources.splitlines()), 2)
                self.assertEqual(headers[-1], 'Source File')

    def test_empty_unavailable_and_single_origin_no_extra_column(self):
        with tempfile.TemporaryDirectory() as folder:
            empty = make_database(pathlib.Path(folder) / 'empty/ramdochatV2.db', empty=True)
            good = make_database(pathlib.Path(folder) / 'good/ramdochatV2.db')
            def opener(path):
                return None if path == str(empty) else open_sqlite_db_readonly(path)
            for parser in PARSERS:
                with patch('scripts.artifacts.RandoChat.open_sqlite_db_readonly', side_effect=opener), patch('scripts.artifacts.RandoChat.check_in_media', return_value='ref'):
                    headers, rows, _ = parser.__wrapped__(context(folder, [empty, good]))
                self.assertTrue(rows)
                self.assertNotIn('Source File', headers)
                headers, rows, _ = parser.__wrapped__(context(folder, [empty]))
                self.assertNotIn('Source File', headers)
                self.assertEqual(len(rows), 1 if parser is randochat_account else 0)
                self.assertEqual(parser.__wrapped__(context(folder, [str(good) + '-wal']))[1], [])

    def test_missing_required_column_then_valid_account(self):
        with tempfile.TemporaryDirectory() as folder:
            thin = pathlib.Path(folder) / 'thin/ramdochatV2.db'
            thin.parent.mkdir()
            con = sqlite3.connect(thin)
            con.execute('CREATE TABLE configuracao(name)')
            con.close()
            good = make_database(pathlib.Path(folder) / 'good/ramdochatV2.db')
            with patch('scripts.artifacts.RandoChat.logfunc') as log:
                headers, rows, _ = randochat_account.__wrapped__(context(folder, [thin, good]))
            self.assertEqual(len(rows), 1)
            self.assertNotIn('Source File', headers)
            self.assertTrue(any('missing value' in call.args[0] and 'thin/' in call.args[0] for call in log.call_args_list))
