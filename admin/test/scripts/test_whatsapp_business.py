"""WhatsApp Business artifacts must read com.whatsapp.w4b and never com.whatsapp.

The Business artifacts run the WhatsApp artifacts of the same name, so the two apps are told
apart only by the ``paths`` of each artifact. These tests check that on a device holding both
apps each app's artifacts match only that app's files, that the conversation views stay equal
to the WhatsApp ones they were copied from, and that a Business run reads the Business stores
(synthetic databases built here, no real evidence bytes).
"""
import fnmatch
import os
import sqlite3
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, REPO_ROOT)

from scripts.context import Context  # noqa: E402  pylint: disable=wrong-import-position
from scripts.artifacts import WhatsApp, WhatsAppBusiness  # noqa: E402  pylint: disable=wrong-import-position

BUSINESS = WhatsAppBusiness.__artifacts_v2__
STANDARD = WhatsApp.__artifacts_v2__
PREFIX = 'get_whatsapp_business_'

# Both apps' stores as an extraction lists them (Android 11 and later media folders).
FILES = [
    'root/Dump/data/data/com.whatsapp/databases/msgstore.db',
    'root/Dump/data/data/com.whatsapp/databases/msgstore.db-wal',
    'root/Dump/data/data/com.whatsapp/databases/wa.db',
    'root/Dump/data/data/com.whatsapp/files/Avatars/120363000000000001@g.us.j',
    'root/Dump/data/data/com.whatsapp/shared_prefs/com.whatsapp_preferences_light.xml',
    'root/Dump/data/data/com.whatsapp/shared_prefs/startup_prefs.xml',
    'root/Dump/sdcard/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images/IMG-1.jpg',
    'root/Dump/data/data/com.whatsapp.w4b/databases/msgstore.db',
    'root/Dump/data/data/com.whatsapp.w4b/databases/msgstore.db-wal',
    'root/Dump/data/data/com.whatsapp.w4b/databases/wa.db',
    'root/Dump/data/data/com.whatsapp.w4b/files/Avatars/120363000000000001@g.us.j',
    'root/Dump/data/data/com.whatsapp.w4b/shared_prefs/com.whatsapp_preferences_light.xml',
    'root/Dump/data/data/com.whatsapp.w4b/shared_prefs/startup_prefs.xml',
    'root/Dump/sdcard/Android/media/com.whatsapp.w4b/WhatsApp Business/Media/WhatsApp Business Images/IMG-2.jpg',
]


def _matches(artifact):
    paths = artifact['paths']
    return [f for f in FILES if any(fnmatch.fnmatchcase(f, p) for p in paths)]


class WhatsAppBusinessPathsTest(unittest.TestCase):

    def test_every_whatsapp_artifact_has_a_business_twin(self):
        self.assertEqual(
            sorted(k[len(PREFIX):] for k in BUSINESS),
            sorted(k[len('get_whatsapp_'):] for k in STANDARD))

    def test_business_paths_match_only_business_files(self):
        for key, info in BUSINESS.items():
            matched = _matches(info)
            self.assertTrue(matched, key)
            for path in matched:
                self.assertIn('w4b', path, key)

    def test_whatsapp_paths_match_no_business_file(self):
        for key, info in STANDARD.items():
            for path in _matches(info):
                self.assertNotIn('w4b', path, key)

    def test_conversation_views_equal_the_whatsapp_views(self):
        for key, info in BUSINESS.items():
            twin = STANDARD['get_whatsapp_' + key[len(PREFIX):]]
            self.assertEqual(info.get('data_views'), twin.get('data_views'), key)

    def test_each_function_is_a_distinct_artifact_processor(self):
        for key in BUSINESS:
            self.assertTrue(hasattr(getattr(WhatsAppBusiness, key), '__wrapped__'), key)


class WhatsAppBusinessRunTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_folder = os.path.join(self.tmp.name, 'report', 'data')
        Context.set_data_folder(self.data_folder)

    def tearDown(self):
        Context.clear()
        self.tmp.cleanup()

    def _store(self, package, text):
        folder = os.path.join(self.data_folder, 'Dump', 'data', 'data', package, 'databases')
        os.makedirs(folder)
        msgstore = os.path.join(folder, 'msgstore.db')
        con = sqlite3.connect(msgstore)
        con.execute('CREATE TABLE jid(_id INTEGER PRIMARY KEY, user TEXT, server TEXT, raw_string TEXT)')
        con.execute('CREATE TABLE chat(_id INTEGER PRIMARY KEY, jid_row_id INTEGER, subject TEXT)')
        con.execute('CREATE TABLE message(_id INTEGER PRIMARY KEY, chat_row_id INTEGER, from_me INTEGER, '
                    'timestamp INTEGER, received_timestamp INTEGER, message_type INTEGER, text_data TEXT, '
                    'sender_jid_row_id INTEGER)')
        con.execute('CREATE TABLE message_media(message_row_id INTEGER, file_path TEXT, file_size INTEGER)')
        con.execute('CREATE TABLE message_location(message_row_id INTEGER, latitude REAL, longitude REAL, '
                    'live_location_share_duration INTEGER, live_location_final_latitude REAL, '
                    'live_location_final_longitude REAL, live_location_final_timestamp INTEGER)')
        con.execute("INSERT INTO jid VALUES (1, '15550100001', 's.whatsapp.net', '15550100001@s.whatsapp.net')")
        con.execute('INSERT INTO chat VALUES (1, 1, NULL)')
        con.execute('INSERT INTO message VALUES (1, 1, 0, 1760000000000, 1760000000000, 0, ?, NULL)', (text,))
        con.commit()
        con.close()
        return msgstore

    def test_each_app_reports_only_its_own_store(self):
        standard = self._store('com.whatsapp', 'standard app message')
        business = self._store('com.whatsapp.w4b', 'business app message')
        files = [standard, business]
        for module, artifact, expected in (
                (WhatsApp, 'get_whatsapp_one_to_one_messages', 'standard app message'),
                (WhatsAppBusiness, 'get_whatsapp_business_one_to_one_messages', 'business app message')):
            info = module.__artifacts_v2__[artifact]
            # The seeker gives an artifact the files its own paths match.
            found = [f for f in files if any(
                fnmatch.fnmatchcase('root/' + os.path.relpath(f, self.data_folder).replace(os.sep, '/'), p)
                for p in info['paths'])]
            Context.set_files_found(found)
            _headers, rows, source = getattr(module, artifact).__wrapped__(Context)
            self.assertEqual([r[5] for r in rows], [expected], artifact)
            self.assertEqual(source, found[0], artifact)


if __name__ == '__main__':
    unittest.main()
