"""Messenger storage aliases and source-scoped record identity regressions."""
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from scripts.artifacts import FacebookMessenger as messenger

KEYS = tuple(messenger.__artifacts_v2__)


def create_fixture(root):
    root = Path(root)
    for scope in ['A/data/data', 'A/data/user/10', 'B/data/data', 'unknown']:
        folder = root/scope/'com.facebook.orca/databases'
        folder.mkdir(parents=True, exist_ok=True)
        (folder/'threads_db2-uid').write_text('42\n42\n', encoding='utf-8')
        db = sqlite3.connect(folder/'msys_database_42')
        db.executescript('''
CREATE TABLE _user_info(facebook_user_id); INSERT INTO _user_info VALUES(42);
CREATE TABLE contacts(id,name,normalized_name_for_search,username,profile_picture_large_url,email_address,phone_number,is_messenger_user,friendship_status,birthday_timestamp);
INSERT INTO contacts VALUES(42,'name','name','user','pic','email','phone',1,0,0);
CREATE TABLE messages(timestamp_ms,sender_id,thread_key,text,is_admin_message,message_id);
INSERT INTO messages VALUES(1700000000000,42,'thread','same <message>',0,'m1');
CREATE TABLE attachments(message_id,title_text,subtitle_text,filename,playable_url_mime_type,playable_url);
INSERT INTO attachments VALUES('m1','title','subtitle','image','image/jpeg','url');
CREATE TABLE attachment_ctas(message_id,native_url);
CREATE TABLE reactions(message_id,reaction,reaction_creation_timestamp_ms);
INSERT INTO reactions VALUES('m1','like',1700000001000);
CREATE TABLE call_log(call_timestamp_ms,call_duration,call_direction,call_media_type,has_been_seen,thread_key);
INSERT INTO call_log VALUES(1700000000000,5,1,2,0,42);
''')
        db.close()
        db = sqlite3.connect(folder/'threads_db2')
        db.executescript('''
CREATE TABLE threads(thread_key); INSERT INTO threads VALUES('thread');
CREATE TABLE messages(timestamp_ms,sender,thread_key,text,snippet,attachments,shares,msg_id,generic_admin_message_extensible_data,msg_type);
INSERT INTO messages VALUES(1700000000000,'{"name":"name","user_key":"FACEBOOK:42"}','thread','legacy <message>','snippet','[{"filename":"file"}]','[{"name":"share","description":"desc","href":"link"}]','l1',NULL,0);
INSERT INTO messages VALUES(1700000000000,'{"name":"name","user_key":"FACEBOOK:42"}','thread',NULL,NULL,NULL,NULL,'c1','{"call_duration":5,"caller_id":42,"video":false}',0);
CREATE TABLE message_reactions(msg_id,reaction,reaction_timestamp);
INSERT INTO message_reactions VALUES('l1','like',1700000001000);
CREATE TABLE thread_users(user_key,first_name,last_name,username,profile_pic_square,is_messenger_user,is_friend,friendship_status,contact_relationship_status);
INSERT INTO thread_users VALUES('FACEBOOK:42','first','last','user','[]',1,1,0,0);
''')
        db.close()
    original = root/'A/data/data/com.facebook.orca/databases'
    for alias in ['A/data/user/0/com.facebook.orca/databases', 'A/data_mirror/data_ce/null/0/com.facebook.orca/databases']:
        shutil.copytree(original, root/alias)
    copy = root/'A/data/data/com.facebook.katana/app_mib_msys/v2/42'
    copy.mkdir(parents=True)
    shutil.copy2(original/'msys_database_42', copy/'msys_database_42')
    db = sqlite3.connect(copy/'msys_database_42')
    db.execute("UPDATE attachments SET playable_url='other-url'")
    db.execute("UPDATE contacts SET profile_picture_large_url='other-pic'")
    db.commit()
    db.close()
    second = root/'unknown-second/msys_database_42'
    second.parent.mkdir()
    shutil.copy2(original/'msys_database_42', second)
    return [p for p in root.rglob('*') if p.is_file()]


class Context:
    def __init__(self, root, files):
        self.root, self.files = Path(root), files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))

    def get_seeker(self):
        return None


def run(root, files, key):
    context = Context(root, files)
    with patch.object(messenger.Context, 'get_relative_path', side_effect=context.get_relative_path):
        headers, rows, _source = getattr(messenger, key).__wrapped__(context)
    return [h[0] if isinstance(h, tuple) else h for h in headers], rows


class TestMessengerEvidenceScope(unittest.TestCase):
    def test_all_artifacts_survive_staging_names_and_distinct_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            normal = Path(directory)/'normal'
            files = create_fixture(normal)
            expected = {}
            for key in KEYS:
                headers, rows = run(normal, files, key)
                expected[key] = rows
                self.assertEqual(len(rows), 5 if 'msys' in key else 8 if 'user_id' in key else 4)
                source_index = headers.index('Source File')
                self.assertTrue(all(not Path(r[source_index]).is_absolute() for r in rows))
                if 'msys' in key:
                    self.assertEqual(sum('com.facebook.katana' in r[-1] for r in rows), 1)
                    self.assertTrue(any('data/user/10/' in r[-1] for r in rows))
                    self.assertEqual(sum(r[-1].startswith('unknown') for r in rows), 2)
            for name in ['mirror-staging', 'staged/user/0']:
                staged = Path(directory)/name
                shutil.copytree(normal, staged)
                copied = [staged/p.relative_to(normal) for p in files]
                for key in KEYS:
                    self.assertEqual(run(staged, copied, key)[1], expected[key])

    def test_differing_records_within_known_namespace_survive(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_fixture(directory)
            copied = next(p for p in files if 'katana/' in str(p))
            db = sqlite3.connect(copied)
            db.execute("INSERT INTO messages VALUES(1700000002000,42,'thread','only in copy',0,'m2')")
            db.execute("INSERT INTO call_log VALUES(1700000002000,9,2,1,1,42)")
            db.execute("INSERT INTO contacts SELECT 43,'other',normalized_name_for_search,"
                       "username,profile_picture_large_url,email_address,phone_number,"
                       "is_messenger_user,friendship_status,birthday_timestamp FROM contacts")
            db.commit()
            db.close()
            for key in KEYS:
                if 'msys' not in key:
                    continue
                headers, rows = run(directory, files, key)
                self.assertEqual(len(rows), 6)
                exclusive = [row for row in rows if 'katana/' in row[-1] and '; ' not in row[-1]]
                self.assertEqual(len(exclusive), 1)
                if key == 'get_fb_msys_chats':
                    self.assertEqual(exclusive[0][headers.index('Message')], 'only in copy')

    def test_mirror_only_and_dates_keep_values(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_fixture(directory)
            mirror = [p for p in files if 'data_mirror/' in str(p)]
            for key in KEYS:
                headers, rows = run(directory, mirror, key)
                self.assertEqual(len(rows), 2 if 'user_id' in key else 1)
                if key == 'get_fb_threads_chats':
                    self.assertEqual(headers[:2], ['Timestamp', 'Message Reaction Timestamp'])
                    self.assertEqual(rows[0][1].timestamp(), 1700000001)
                    self.assertEqual(rows[0][headers.index('Message')], 'legacy <message>')
                if key == 'get_fb_msys_contacts':
                    self.assertEqual(headers[:2], ['Birthdate (MM-DD)', 'Birthday Timestamp (as stored)'])
                    self.assertEqual(rows[0][:2], ('01-01', 0))


if __name__ == '__main__':
    unittest.main()
