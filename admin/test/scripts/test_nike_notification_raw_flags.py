"""Valid WAL evidence tests main-file selection and distinct stored flag values."""
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from scripts.artifacts import NikeNotifications as nike
from admin.test.scripts.test_history_doclist_all_sources import Context

FLAGS=[(None,None),(0,0),(1,1),(2,-1),('unknown',''),(None,None)]


def create_notification_fixture(root,empty=False):
    folder=Path(root)/'data/data/com.nike.plusgps/databases';folder.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as live:
        live=Path(live);path=live/'ns_inbox.db';db=sqlite3.connect(path)
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('CREATE TABLE inbox(_id,sender_user_id,sender_app_id,notification_timestamp,notification_type,message,read,deleted)')
        db.commit();db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        for index,(read,deleted) in enumerate([] if empty else FLAGS):
            if index==5:index=0
            db.execute('INSERT INTO inbox VALUES(?,?,?,?,?,?,?,?)',(index,'sender','app',1700000000000+index*1000,'source type','<raw> é: text',read,deleted))
        db.commit()
        for source in live.iterdir():shutil.copy2(source,folder/source.name)
        db.close()
    return str(folder/'ns_inbox.db')


class TestNikeNotificationRawFlags(unittest.TestCase):
    def test_actual_wal_sidecar_first_raw_flags_and_repeats(self):
        with tempfile.TemporaryDirectory() as root:
            path=create_notification_fixture(root)
            main=sqlite3.connect(Path(path).as_uri()+'?immutable=1',uri=True)
            self.assertEqual(main.execute('SELECT count(*) FROM inbox').fetchone()[0],0);main.close()
            source=sqlite3.connect(Path(path).as_uri()+'?mode=ro',uri=True)
            stored=source.execute('SELECT _id,sender_user_id,sender_app_id,notification_timestamp,notification_type,message,read,deleted FROM inbox').fetchall();source.close()
            with patch.object(nike,'open_sqlite_db_readonly',wraps=nike.open_sqlite_db_readonly) as opened:
                headers,rows,_=nike.get_nike_notifications.__wrapped__(Context(root,[path+'-wal',path+'-shm',path+'-journal',path]))
            self.assertEqual(opened.call_args.args[0],path)
            self.assertEqual(headers[0],('Notification Timestamp','datetime'))
            self.assertEqual(len(rows),6)
            self.assertEqual(rows[0],rows[-1])
            for row,actual in zip(rows,stored):
                self.assertEqual(row[1:4],actual[:3]);self.assertEqual(row[4:],actual[4:])
                self.assertEqual(row[0].timestamp(),actual[3]/1000)
                self.assertEqual([type(v) for v in row[-2:]],[type(v) for v in actual[-2:]])

    def test_sidecars_only_never_opened_and_empty_main_valid(self):
        with tempfile.TemporaryDirectory() as root:
            path=create_notification_fixture(root,empty=True)
            with patch.object(nike,'open_sqlite_db_readonly') as opened,patch.object(nike,'logfunc') as log:
                self.assertEqual(nike.get_nike_notifications.__wrapped__(Context(root,[path+'-wal',path+'-shm']))[1],[])
            opened.assert_not_called()
            self.assertTrue(any('no exact ns_inbox.db main' in str(call) for call in log.call_args_list))
            self.assertEqual(nike.get_nike_notifications.__wrapped__(Context(root,[path]))[1],[])
