"""A Gboard training cache payload that does not decode costs only what that payload held.

On pixel3_a11, 4 of the 207 payloads in trainingcache2.db did not decode. Before the fix a
DecodeError stopped the keystrokes artifact. A ValueError ended the read of that database at
that row.
"""
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import blackboxprotobuf  # pylint: disable=wrong-import-position
from scripts.artifacts.gboard import _events_trainingcache2, _events_trainingcachev2  # pylint: disable=wrong-import-position

TYPEDEF = {'7': {'type': 'message', 'name': '', 'message_typedef': {
    '2': {'type': 'message', 'name': '', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}}}}}}
# A length-delimited field 7 whose length runs past the end of the payload.
TRUNCATED = b'\x3a\x10\x12\x02\x0a'


def _payload(text):
    return blackboxprotobuf.encode_message({'7': {'2': {'1': text}}}, TYPEDEF)


class TestGboardBadPayload(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _cache2(self, payloads):
        path = pathlib.Path(self.tmpdir) / 'trainingcache2.db'
        db = sqlite3.connect(path)
        db.execute('CREATE TABLE training_input_events_table (_id INTEGER, _payload BLOB, f2 TEXT, f4 TEXT, '
                   'f5 TEXT, f9 INTEGER)')
        for number, payload in enumerate(payloads, 1):
            db.execute('INSERT INTO training_input_events_table VALUES (?, ?, "app", "box", "id", 1700000000000)',
                       (number, payload))
        db.commit()
        db.close()
        return str(path)

    def test_a_bad_payload_keeps_its_row_and_the_rows_after_it(self):
        events = _events_trainingcache2(self._cache2([_payload(b'first'), TRUNCATED, _payload(b'third')]))
        self.assertEqual([(event.id, event.text) for event in events], [(1, 'first'), (2, ''), (3, 'third')])
        self.assertEqual(events[1].app, 'app')

    def test_v2_skips_a_bad_payload_and_reads_the_rest(self):
        path = pathlib.Path(self.tmpdir) / 'trainingcachev2.db'
        db = sqlite3.connect(path)
        db.execute('CREATE TABLE input_action_table (_id INTEGER, _payload BLOB, _timestamp INTEGER, _session_id INTEGER)')
        db.execute('CREATE TABLE session_table (_id INTEGER, _payload BLOB, _timestamp INTEGER, _session_id INTEGER)')
        typedef = {'6': {'type': 'message', 'name': '', 'message_typedef': {
            '4': {'type': 'message', 'name': '', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}}}}}}
        good = blackboxprotobuf.encode_message({'6': {'4': {'1': b'ok'}}}, typedef)
        db.execute('INSERT INTO session_table VALUES (1, ?, 1700000000000, 1)', (TRUNCATED,))
        # Field 6 holding bytes where a message is expected decodes without an error.
        not_a_message = b'\x32\x02\x22\x01'
        for number, payload in enumerate([good, TRUNCATED, not_a_message, good], 1):
            db.execute('INSERT INTO input_action_table VALUES (?, ?, 1700000000000, 1)', (number, payload))
        db.commit()
        db.close()
        events = _events_trainingcachev2(str(path))
        self.assertEqual([event.text for event in events], ['okok'])


if __name__ == '__main__':
    unittest.main()
