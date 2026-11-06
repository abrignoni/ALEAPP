"""Private Notepad on synthetic data built by running the app's encryption chain in reverse.

Each test writes a real notes.db, preferences file and attachment files to a temporary folder:
a data key is wrapped under the static key, and text and files are encrypted under the data key.
The schema is the one the parser queries, not one observed on a device, so these tests prove
the parser handles this scheme and say nothing about what an installed app writes.

The fixture encrypts on its own and holds the static key as a known answer. Taking the key from
get_static_key() would let a wrong key pass, since both sides would then agree on it.
"""
import ast
import base64
import fnmatch
import hashlib
import json
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch
from xml.sax.saxutils import escape, quoteattr

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from Crypto.Cipher import AES  # pylint: disable=wrong-import-position
from Crypto.Util.Padding import pad  # pylint: disable=wrong-import-position
from scripts.artifacts import privateNotepad as parser  # pylint: disable=wrong-import-position

MODULE = 'scripts.artifacts.privateNotepad'
PACKAGE = 'ru.alexandermalikov.protectednotes'
USER_0 = f'data/data/{PACKAGE}'
USER_10 = f'data/user/10/{PACKAGE}'
DATABASE = 'databases/notes.db'
PREFERENCES = 'shared_prefs/protected_notes_preferences.xml'

STATIC_KEY = bytes.fromhex('e16245b64c30509a931ddf9d24db406b')
DATA_KEY = bytes(range(16))
OTHER_KEY = bytes(range(16, 32))
ZERO_IV = b'\x00' * 16

PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')
MP3 = b'ID3\x03\x00\x00\x00\x00\x00\x00' + b'\x00' * 32
JPEG = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00' + b'\x00' * 32
INTRUDER = f'{USER_0}/files/intruder_photos'

NOTE_COLUMNS = ('_id', 'date', 'date_created', 'date_delete', 'title', 'note', 'images',
                'audio_files')
PASSWORD_COLUMNS = ('_id', 'date_created', 'password_name', 'password_login', 'password_password',
                    'password_site_address', 'password_comment')

MS_1 = 1700000000000
UTC_1 = datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc)
MS_2 = 1600000000123
UTC_2 = datetime(2020, 9, 13, 12, 26, 40, 123000, tzinfo=timezone.utc)


def encrypt(key, plain):
    return AES.new(key, AES.MODE_CBC, ZERO_IV).encrypt(pad(plain, AES.block_size))


def wrap(data_key, under=STATIC_KEY):
    """A data key as service_data.dek and the encryption_key preference hold it."""
    return base64.b64encode(encrypt(under, data_key)).decode('ascii')


def text(value, key=DATA_KEY):
    """A text field as the notes and passwords tables hold it."""
    return base64.b64encode(encrypt(key, value.encode('utf-8'))).decode('ascii')


def note(pk=1, title='Title', body='Body', key=DATA_KEY, **columns):
    return {'_id': pk, 'title': text(title, key), 'note': text(body, key), **columns}


def ids(*values, name='image_ids'):
    return json.dumps({name: list(values)})


class Extraction:
    """A temporary folder holding the app's files at the paths an extraction would."""

    def __init__(self, root):
        self.root = pathlib.Path(root)
        self.files = []

    def add(self, relative, data=b''):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        self.files.append(path)
        return path

    def attachment(self, name, plain=PNG, key=DATA_KEY, app=USER_0, folder='images'):
        return self.add(f'{app}/files/{folder}/{name}', encrypt(key, plain))

    def database(self, app=USER_0, notes=(), passwords=None, dek=None, note_columns=NOTE_COLUMNS):
        path = self.add(f'{app}/{DATABASE}')
        db = sqlite3.connect(path)
        try:
            if note_columns:
                db.execute(f'CREATE TABLE notes ({", ".join(note_columns)})')
                self._insert(db, 'notes', note_columns, notes)
            if passwords is not None:
                db.execute(f'CREATE TABLE passwords ({", ".join(PASSWORD_COLUMNS)})')
                self._insert(db, 'passwords', PASSWORD_COLUMNS, passwords)
            if dek is not None:
                db.execute('CREATE TABLE service_data (dek TEXT)')
                db.execute('INSERT INTO service_data VALUES (?)', (dek,))
            db.commit()
        finally:
            db.close()
        return path

    @staticmethod
    def _insert(db, table, columns, rows):
        marks = ', '.join('?' for _ in columns)
        for row in rows:
            db.execute(f'INSERT INTO {table} VALUES ({marks})', [row.get(c) for c in columns])

    def preferences(self, app=USER_0, strings=None, typed=None, raw=None):
        """strings become <string> elements; typed {name: (tag, value)} carry a value attribute."""
        elements = [f'<string name={quoteattr(k)}>{escape(v)}</string>'
                    for k, v in (strings or {}).items()]
        elements += [f'<{tag} name={quoteattr(k)} value={quoteattr(v)} />'
                     for k, (tag, v) in (typed or {}).items()]
        body = raw if raw is not None else f'<map>{"".join(elements)}</map>'
        return self.add(f'{app}/{PREFERENCES}', body.encode('utf-8'))

    def context(self):
        return SimpleNamespace(
            get_files_found=lambda: [str(p) for p in self.files],
            get_relative_path=lambda p: pathlib.Path(p).relative_to(self.root).as_posix())


class PrivateNotepadCase(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.extraction = Extraction(folder.name)
        self.media = []

        def check_in(path, data, name, **kwargs):
            self.media.append(SimpleNamespace(path=path, data=data, name=name, kwargs=kwargs))
            return f'ref:{name}'

        def check_in_file(path, name, **kwargs):
            self.media.append(SimpleNamespace(path=path, data=None, name=name, kwargs=kwargs))
            return f'ref:{name}'

        media = patch(f'{MODULE}.check_in_embedded_media', side_effect=check_in)
        media.start()
        self.addCleanup(media.stop)
        file_media = patch(f'{MODULE}.check_in_media', side_effect=check_in_file)
        file_media.start()
        self.addCleanup(file_media.stop)
        log = patch(f'{MODULE}.logfunc')
        self.log = log.start()
        self.addCleanup(log.stop)

    def run_artifact(self, artifact):
        """(rows, sources) of an artifact, with every row as wide as the headers."""
        headers, rows, sources = artifact.__wrapped__(self.extraction.context())
        for row in rows:
            self.assertEqual(len(row), len(headers), row)
        return rows, [s for s in sources.split('\n') if s]

    def logged(self):
        return '\n'.join(str(call.args[0]) for call in self.log.call_args_list)


class CryptoTest(PrivateNotepadCase):
    def test_static_key_is_the_known_answer_and_is_built_once(self):
        self.assertEqual(parser.get_static_key(), STATIC_KEY)
        self.assertIs(parser.get_static_key(), parser.get_static_key())

    def test_decrypt_reverses_the_fixture_with_a_zero_iv(self):
        self.assertEqual(parser.aes_cbc_decrypt(DATA_KEY, encrypt(DATA_KEY, b'plain')), b'plain')
        # Under another IV only the first block comes out wrong, so the padding still passes
        plain = b'first block here' + b'second block'
        other_iv = AES.new(DATA_KEY, AES.MODE_CBC, b'\x01' * 16).encrypt(pad(plain, 16))
        self.assertEqual(parser.aes_cbc_decrypt(DATA_KEY, other_iv)[16:], b'second block')
        self.assertNotEqual(parser.aes_cbc_decrypt(DATA_KEY, other_iv), plain)

    def test_field_decrypts_including_non_ascii_text(self):
        for value in ('Indkøb æøå', 'Тайная заметка', '日本語', 'x' * 16):
            with self.subTest(value=value):
                self.assertEqual(parser.decrypt_field(DATA_KEY, text(value), 'title', 'n'), value)

    def test_empty_field_stays_as_stored_and_logs_nothing(self):
        for value in (None, ''):
            self.assertEqual(parser.decrypt_field(DATA_KEY, value, 'title', 'n'), value)
        self.log.assert_not_called()

    def test_field_that_does_not_decrypt_is_returned_as_stored_and_logged(self):
        cases = {
            'another key': text('secret', OTHER_KEY),
            'not base64': 'not base64!!',
            'not a block multiple': base64.b64encode(b'short').decode('ascii'),
            'bad UTF-8': base64.b64encode(encrypt(DATA_KEY, b'\xff\xfe')).decode('ascii'),
        }
        for label, stored in cases.items():
            with self.subTest(label):
                self.log.reset_mock()
                self.assertEqual(parser.decrypt_field(DATA_KEY, stored, 'title', 'note 7'), stored)
                self.assertIn('title of note 7 did not decrypt', self.logged())


class HelperTest(PrivateNotepadCase):
    def test_times_are_milliseconds_in_utc_and_null_or_zero_is_blank(self):
        self.assertEqual(parser.convert_ms_to_utc(MS_1), UTC_1)
        self.assertEqual(parser.convert_ms_to_utc(str(MS_2)), UTC_2)
        self.assertIsNone(parser.convert_ms_to_utc(None))
        self.assertIsNone(parser.convert_ms_to_utc(0))

    def test_attachment_ids_come_from_every_list_of_the_json(self):
        cases = (
            (None, []),
            ('', []),
            ('{"image_ids": ["a", "b"]}', ['a', 'b']),
            ('{"one": ["a"], "two": [1], "flag": true}', ['a', '1']),
            ('["a", "b"]', ['a', 'b']),
            ('{"image_ids": ["", null, "a"]}', ['a']),
            ('{"image_ids": "a"}', []),
        )
        for stored, expected in cases:
            with self.subTest(stored=stored):
                self.assertEqual(parser.attachment_ids(stored), expected)
        self.log.assert_not_called()

    def test_attachment_list_that_is_not_json_is_logged(self):
        self.assertEqual(parser.attachment_ids('{broken'), [])
        self.assertIn('not JSON', self.logged())

    def test_preferences_read_values_and_text(self):
        path = self.extraction.preferences(strings={'hint': 'a & b'},
                                           typed={'count': ('int', '3')})
        self.assertEqual(parser.get_preferences(path),
                         {'hint': ('string', 'a & b'), 'count': ('int', '3')})

    def test_preferences_that_cannot_be_used_return_none(self):
        cases = {'not xml': '<map><string', 'wrong root': '<other />'}
        for label, raw in cases.items():
            with self.subTest(label):
                self.log.reset_mock()
                path = self.extraction.preferences(raw=raw)
                self.assertIsNone(parser.get_preferences(path))
                self.assertIn('Private Notepad', self.logged())
        self.assertIsNone(parser.get_preferences(str(self.extraction.root / 'absent.xml')))

    def test_attachment_over_the_size_limit_is_not_read(self):
        path = self.extraction.attachment('big')
        with patch(f'{MODULE}.MAX_ATTACHMENT_SIZE', 1):
            self.assertIsNone(parser.decrypt_attachment(DATA_KEY, path))
        self.assertIn('larger than', self.logged())
        self.assertEqual(parser.decrypt_attachment(DATA_KEY, path), PNG)

    def test_attachment_that_does_not_decrypt_returns_none(self):
        other = self.extraction.attachment('other', key=OTHER_KEY)
        plain = self.extraction.add(f'{USER_0}/files/plain', PNG)
        self.assertIsNone(parser.decrypt_attachment(DATA_KEY, other))
        self.assertIsNone(parser.decrypt_attachment(DATA_KEY, plain))
        self.assertIsNone(parser.decrypt_attachment(DATA_KEY, str(self.extraction.root / 'absent')))


class KeyResolutionTest(PrivateNotepadCase):
    def key_source(self):
        rows, _ = self.run_artifact(parser.private_notepad_settings)
        return rows[0][6]

    def titles(self):
        rows, _ = self.run_artifact(parser.private_notepad_notes)
        return [row[3] for row in rows]

    def test_key_in_the_database_only(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note()])
        self.extraction.preferences()
        self.assertEqual(self.key_source(), 'service_data.dek')
        self.assertEqual(self.titles(), ['Title'])

    def test_key_in_the_preferences_only(self):
        self.extraction.database(notes=[note()])
        self.extraction.preferences(strings={'encryption_key': wrap(DATA_KEY)})
        self.assertEqual(self.key_source(), 'encryption_key preference')
        self.assertEqual(self.titles(), ['Title'])

    def test_database_is_tried_first_when_both_decrypt(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note()])
        self.extraction.preferences(strings={'encryption_key': wrap(DATA_KEY)})
        self.assertEqual(self.key_source(), 'service_data.dek')

    def test_key_that_does_not_decrypt_the_notes_gives_way_to_the_next(self):
        self.extraction.database(dek=wrap(OTHER_KEY), notes=[note()])
        self.extraction.preferences(strings={'encryption_key': wrap(DATA_KEY)})
        self.assertEqual(self.key_source(), 'encryption_key preference')
        self.assertEqual(self.titles(), ['Title'])
        self.assertIn('service_data.dek does not decrypt the notes', self.logged())

    def test_preference_key_that_does_not_decrypt_the_notes_is_not_used(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note()])
        self.extraction.preferences(strings={'encryption_key': wrap(OTHER_KEY)})
        self.assertEqual(self.key_source(), 'service_data.dek')

    def test_key_is_tested_on_the_body_when_the_first_title_is_empty(self):
        self.extraction.database(dek=wrap(OTHER_KEY), notes=[{'_id': 1, 'title': '', 'note': text('Body')}])
        self.extraction.preferences(strings={'encryption_key': wrap(DATA_KEY)})
        self.assertEqual(self.key_source(), 'encryption_key preference')

    def test_key_is_tested_on_passwords_when_there_are_no_notes(self):
        self.extraction.database(dek=wrap(OTHER_KEY), passwords=[
            {'_id': 1, 'password_name': text('Bank')}])
        self.extraction.preferences(strings={'encryption_key': wrap(DATA_KEY)})
        self.assertEqual(self.key_source(), 'encryption_key preference')

    def test_first_key_is_used_when_nothing_is_stored_to_test_it_on(self):
        self.extraction.database(dek=wrap(OTHER_KEY))
        self.extraction.preferences(strings={'encryption_key': wrap(DATA_KEY)})
        self.assertEqual(self.key_source(), 'service_data.dek')

    def test_stored_values_that_are_no_key_are_skipped(self):
        cases = {
            'not base64': 'not base64!!',
            'wrapped under another key': wrap(DATA_KEY, under=OTHER_KEY),
            'not a key length': wrap(b'short'),
        }
        for label, dek in cases.items():
            with self.subTest(label):
                self.setUp()
                self.extraction.database(dek=dek, notes=[note()])
                self.extraction.preferences(strings={'encryption_key': wrap(DATA_KEY)})
                self.assertEqual(self.key_source(), 'encryption_key preference')

    def test_value_of_no_key_length_is_refused_when_nothing_is_stored_to_test_it_on(self):
        self.extraction.database(dek=wrap(b'short'))
        self.extraction.preferences(strings={'encryption_key': wrap(DATA_KEY)})
        self.assertEqual(self.key_source(), 'encryption_key preference')
        self.assertIn('is 5 bytes; not used', self.logged())

    def test_key_lengths_aes_accepts_are_used(self):
        for length in (16, 24, 32):
            with self.subTest(length=length):
                self.setUp()
                key = bytes(range(length))
                self.extraction.database(dek=wrap(key), notes=[note(key=key)])
                self.assertEqual(self.titles(), ['Title'])

    def test_no_usable_key_gives_no_rows_and_says_so(self):
        self.extraction.database(dek=wrap(OTHER_KEY), notes=[note()])
        self.extraction.preferences()
        self.assertEqual(self.titles(), [])
        self.assertEqual(self.run_artifact(parser.private_notepad_passwords)[0], [])
        self.assertEqual(self.run_artifact(parser.private_notepad_attachments)[0], [])
        self.assertIn('no data key found', self.logged())
        self.assertEqual(self.key_source(), '')


class NotesTest(PrivateNotepadCase):
    def test_full_row(self):
        database = self.extraction.database(dek=wrap(DATA_KEY), notes=[note(
            7, 'Indkøb æøå', 'Тайная заметка', date=MS_1, date_created=MS_2, date_delete=0,
            images=ids('img-1'), audio_files=ids('aud-1', name='audio_ids'))])
        preferences = self.extraction.preferences(strings={'encryption_key': wrap(DATA_KEY)})
        self.extraction.attachment('img-1', PNG)
        self.extraction.attachment('aud-1', MP3, folder='recordings')

        rows, sources = self.run_artifact(parser.private_notepad_notes)

        self.assertEqual(rows, [(UTC_1, UTC_2, None, 'Indkøb æøå', 'Тайная заметка',
                                 ['ref:img-1', 'ref:aud-1'], 7, f'{USER_0}/{DATABASE}')])
        self.assertEqual(sources, [str(database), str(preferences)])
        self.assertEqual([m.data for m in self.media], [PNG, MP3])

    def test_database_without_the_later_columns_leaves_them_blank(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note(date=MS_1)],
                                 note_columns=('_id', 'date', 'title', 'note'))
        rows, _ = self.run_artifact(parser.private_notepad_notes)
        self.assertEqual(rows, [(UTC_1, None, None, 'Title', 'Body', None, 1,
                                 f'{USER_0}/{DATABASE}')])

    def test_field_that_does_not_decrypt_is_reported_as_stored_beside_those_that_do(self):
        stored = text('Unreadable', OTHER_KEY)
        self.extraction.database(dek=wrap(DATA_KEY), notes=[
            note(1), {'_id': 2, 'title': text('Readable'), 'note': stored}])
        rows, _ = self.run_artifact(parser.private_notepad_notes)
        self.assertEqual([(r[3], r[4]) for r in rows], [('Title', 'Body'), ('Readable', stored)])
        self.assertIn('body of note 2 did not decrypt', self.logged())

    def test_null_title_and_body_stay_blank(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[
            note(1), {'_id': 2, 'title': None, 'note': None}])
        rows, _ = self.run_artifact(parser.private_notepad_notes)
        self.assertEqual((rows[1][3], rows[1][4]), (None, None))

    def test_attachment_that_does_not_decrypt_is_left_out_of_the_row(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note(images=ids('good', 'bad'))])
        self.extraction.attachment('good')
        self.extraction.attachment('bad', key=OTHER_KEY)
        rows, _ = self.run_artifact(parser.private_notepad_notes)
        self.assertEqual(rows[0][5], ['ref:good'])

    def test_database_without_the_notes_table_gives_no_rows_and_says_so(self):
        self.extraction.database(dek=wrap(DATA_KEY), note_columns=None)
        rows, _ = self.run_artifact(parser.private_notepad_notes)
        self.assertEqual(rows, [])
        self.assertIn('no notes table', self.logged())

    def test_preferences_without_a_database_give_no_rows_and_say_so(self):
        self.extraction.preferences(strings={'encryption_key': wrap(DATA_KEY)})
        rows, sources = self.run_artifact(parser.private_notepad_notes)
        self.assertEqual((rows, sources), ([], []))
        self.assertIn('no notes.db beside', self.logged())

    def test_no_files_give_no_rows(self):
        self.assertEqual(self.run_artifact(parser.private_notepad_notes), ([], []))


class AttachmentsTest(PrivateNotepadCase):
    def statuses(self):
        rows, _ = self.run_artifact(parser.private_notepad_attachments)
        return [(r[4], r[2]) for r in rows]

    def test_decrypted_row(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[
            note(3, 'Holiday', date=MS_1, images=ids('img-1'))])
        path = self.extraction.attachment('img-1')
        rows, sources = self.run_artifact(parser.private_notepad_attachments)
        self.assertEqual(rows, [(UTC_1, 'ref:img-1', 'Decrypted', 'Image', 'img-1', 3, 'Holiday',
                                 f'{USER_0}/files/images/img-1', f'{USER_0}/{DATABASE}')])
        self.assertIn(str(path), sources)

    def test_type_comes_from_the_decrypted_bytes_not_the_name(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note(
            images=ids('looks.jpg'), audio_files=ids('sound', name='audio_ids'))])
        self.extraction.attachment('looks.jpg', PNG)
        self.extraction.attachment('sound', MP3, folder='recordings')
        rows, _ = self.run_artifact(parser.private_notepad_attachments)
        self.assertEqual([r[3] for r in rows], ['Image', 'Audio'])
        self.assertEqual([m.kwargs for m in self.media], [
            {'force_type': 'image/png', 'force_extension': 'png'},
            {'force_type': 'audio/mpeg', 'force_extension': 'mp3'}])
        self.assertEqual([m.data for m in self.media], [PNG, MP3])

    def test_decrypted_bytes_of_no_known_type_are_still_checked_in(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note(images=ids('unknown'))])
        self.extraction.attachment('unknown', b'nothing recognisable')
        self.assertEqual(self.statuses(), [('unknown', 'Decrypted')])
        self.assertEqual(self.media[0].kwargs, {})
        self.assertEqual(self.media[0].data, b'nothing recognisable')

    def test_named_file_that_does_not_decrypt_is_a_row_with_no_media(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note(images=ids('other', 'plain'))])
        self.extraction.attachment('other', key=OTHER_KEY)
        self.extraction.add(f'{USER_0}/files/images/plain', PNG)
        rows, _ = self.run_artifact(parser.private_notepad_attachments)
        self.assertEqual([(r[4], r[1], r[2]) for r in rows], [('other', None, 'Not decrypted'),
                                                              ('plain', None, 'Not decrypted')])
        self.assertEqual(self.media, [])

    def test_id_with_no_file_is_a_row(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note(5, 'Trip', date=MS_1,
                                                                 images=ids('gone'))])
        rows, _ = self.run_artifact(parser.private_notepad_attachments)
        self.assertEqual(rows, [(UTC_1, None, 'File not found', 'Image', 'gone', 5, 'Trip', '',
                                 f'{USER_0}/{DATABASE}')])

    def test_only_a_file_of_exactly_the_id_is_matched(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note(images=ids('part'))])
        self.extraction.attachment('x_part_y')
        self.assertEqual(self.statuses(), [('part', 'File not found'), ('x_part_y', 'Not named by a note')])

    def test_each_column_is_matched_in_its_own_folder_only(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note(
            images=ids('in-recordings'), audio_files=ids('in-images'))])
        self.extraction.attachment('in-recordings', folder='recordings')
        self.extraction.attachment('in-images')
        self.assertEqual(self.statuses(), [
            ('in-recordings', 'File not found'), ('in-images', 'File not found'),
            ('in-images', 'Not named by a note'), ('in-recordings', 'Not named by a note')])

    def test_every_file_no_note_names_is_a_row(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note(images=ids('named'))])
        self.extraction.attachment('named')
        self.extraction.attachment('orphan')
        self.extraction.attachment('another-key', key=OTHER_KEY)
        self.extraction.attachment('recording', MP3, folder='recordings')
        rows, sources = self.run_artifact(parser.private_notepad_attachments)
        database = f'{USER_0}/{DATABASE}'
        self.assertEqual(rows[1:], [
            (None, 'ref:orphan', 'Not named by a note', 'Image', 'orphan', '', '',
             f'{USER_0}/files/images/orphan', database),
            (None, None, 'Not named by a note', 'Image', 'another-key', '', '',
             f'{USER_0}/files/images/another-key', database),
            (None, 'ref:recording', 'Not named by a note', 'Audio', 'recording', '', '',
             f'{USER_0}/files/recordings/recording', database)])
        self.assertEqual(len(sources), 5)

    def test_other_folders_are_not_attachments(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note(images=ids('img'))])
        encrypted = encrypt(DATA_KEY, PNG)
        for folder in ('databases', 'shared_prefs', 'cache/images', 'files', 'files/image_previews',
                       'files/intruder_photos', 'files/images/nested'):
            self.extraction.add(f'{USER_0}/{folder}/img', encrypted)
        self.assertEqual(self.statuses(), [('img', 'File not found')])

    def test_shared_storage_is_not_read(self):
        for location in ('data/media/0', 'storage/emulated/0', 'media/0', 'sdcard'):
            with self.subTest(location):
                self.setUp()
                self.extraction.database(dek=wrap(DATA_KEY), notes=[note(images=ids('img'))])
                self.extraction.attachment('img', app=f'{location}/Android/data/{PACKAGE}')
                self.assertEqual(self.statuses(), [('img', 'File not found')])

    def test_attachments_without_a_database_give_no_rows_and_say_so(self):
        self.extraction.attachment('img')
        for artifact in (parser.private_notepad_notes, parser.private_notepad_attachments,
                         parser.private_notepad_settings):
            self.assertEqual(self.run_artifact(artifact), ([], []))
        self.assertIn('no notes.db beside the attachment files', self.logged())

    def test_another_users_file_is_not_matched(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note(images=ids('img'))])
        self.extraction.attachment('img', app=USER_10)
        self.extraction.attachment('img', app=f'data/media/10/Android/data/{PACKAGE}')
        self.assertEqual(self.statuses(), [('img', 'File not found')])

    def test_attachment_list_that_is_not_json_gives_no_row_but_keeps_the_note(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note(images='{broken')])
        self.assertEqual(self.statuses(), [])
        rows, _ = self.run_artifact(parser.private_notepad_notes)
        self.assertEqual(rows[0][3], 'Title')


class IntruderPhotosTest(PrivateNotepadCase):
    def test_full_row_needs_no_key_or_database(self):
        path = self.extraction.add(f'{INTRUDER}/{MS_1}.jpg', JPEG)
        rows, sources = self.run_artifact(parser.private_notepad_intruder_photos)
        self.assertEqual(rows, [(UTC_1, f'ref:{MS_1}.jpg', 'Image', f'{MS_1}.jpg', '0',
                                 f'{INTRUDER}/{MS_1}.jpg')])
        self.assertEqual(sources, [str(path)])
        self.assertEqual(self.media[0].kwargs, {'force_type': 'image/jpeg', 'force_extension': 'jpg'})

    def test_type_comes_from_the_bytes_not_the_name(self):
        self.extraction.add(f'{INTRUDER}/{MS_1}.jpg', PNG)
        self.run_artifact(parser.private_notepad_intruder_photos)
        self.assertEqual(self.media[0].kwargs, {'force_type': 'image/png', 'force_extension': 'png'})

    def test_file_that_is_no_image_is_a_row_without_media_and_is_logged(self):
        for label, data in (('encrypted', encrypt(DATA_KEY, JPEG)), ('audio', MP3), ('empty', b'')):
            with self.subTest(label):
                self.setUp()
                self.extraction.add(f'{INTRUDER}/{MS_1}.jpg', data)
                rows, _ = self.run_artifact(parser.private_notepad_intruder_photos)
                self.assertEqual(rows, [(UTC_1, None, 'Not a recognised image', f'{MS_1}.jpg', '0',
                                         f'{INTRUDER}/{MS_1}.jpg')])
                self.assertEqual(self.media, [])
                self.assertIn('not a recognised image', self.logged())

    def test_name_that_is_no_time_leaves_the_time_blank(self):
        for name in ('photo.jpg', 'IMG_20200101.jpg', '-1.jpg', f'{"9" * 40}.jpg'):
            with self.subTest(name):
                self.assertIsNone(parser.file_name_time(name))
        self.assertEqual(parser.file_name_time(f'{MS_2}.jpg'), UTC_2)
        self.assertEqual(parser.file_name_time(str(MS_2)), UTC_2)

    def test_each_android_user_keeps_its_own_photos_and_views_collapse(self):
        for app in (USER_0, f'data/user/0/{PACKAGE}', USER_10):
            self.extraction.add(f'{app}/files/intruder_photos/{MS_1}.jpg', JPEG)
        rows, _ = self.run_artifact(parser.private_notepad_intruder_photos)
        self.assertEqual(sorted(r[4] for r in rows), ['0', '10'])

    def test_files_outside_the_folder_are_not_read(self):
        for path in (f'data/media/0/Android/data/{PACKAGE}/files/intruder_photos/a.jpg',
                     f'{USER_0}/files/images/a.jpg',
                     f'{INTRUDER}/nested/a.jpg',
                     'elsewhere/files/intruder_photos/a.jpg'):
            self.extraction.add(path, JPEG)
        self.assertEqual(self.run_artifact(parser.private_notepad_intruder_photos), ([], []))


class PasswordsTest(PrivateNotepadCase):
    def test_full_row(self):
        database = self.extraction.database(dek=wrap(DATA_KEY), passwords=[{
            '_id': 4, 'date_created': MS_1, 'password_name': text('Bank'),
            'password_login': text('jens@example.invalid'), 'password_password': text('hunter2'),
            'password_site_address': text('https://example.invalid'),
            'password_comment': text('Kommentar æøå')}])
        preferences = self.extraction.preferences(strings={'encryption_key': wrap(DATA_KEY)})
        rows, sources = self.run_artifact(parser.private_notepad_passwords)
        self.assertEqual(rows, [(UTC_1, 'Bank', 'jens@example.invalid', 'hunter2',
                                 'https://example.invalid', 'Kommentar æøå', 4,
                                 f'{USER_0}/{DATABASE}')])
        self.assertEqual(sources, [str(database), str(preferences)])

    def test_field_that_does_not_decrypt_is_reported_as_stored(self):
        stored = text('secret', OTHER_KEY)
        self.extraction.database(dek=wrap(DATA_KEY), passwords=[
            {'_id': 1, 'password_name': text('Bank'), 'password_password': stored}])
        rows, _ = self.run_artifact(parser.private_notepad_passwords)
        self.assertEqual((rows[0][1], rows[0][3], rows[0][4]), ('Bank', stored, None))
        self.assertIn('password of password 1 did not decrypt', self.logged())

    def test_database_without_the_table_gives_no_rows_and_says_so(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note()])
        rows, sources = self.run_artifact(parser.private_notepad_passwords)
        self.assertEqual((rows, sources), ([], []))
        self.assertIn('no passwords table', self.logged())


class SettingsTest(PrivateNotepadCase):
    def row(self):
        rows, _ = self.run_artifact(parser.private_notepad_settings)
        self.assertEqual(len(rows), 1)
        return rows[0]

    def test_full_row(self):
        digest = bytes(range(20))
        fake_digest = bytes(range(20, 40))
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note()])
        path = self.extraction.preferences(
            strings={'password_hint': 'first pet', 'protection_type': '1',
                     'password_hash': base64.b64encode(digest).decode('ascii'),
                     'fake_password_hash': base64.b64encode(fake_digest).decode('ascii')},
            typed={'last_app_usage_time': ('long', str(MS_1)),
                   'show_lock_screen': ('boolean', 'true')})
        rows, sources = self.run_artifact(parser.private_notepad_settings)
        self.assertEqual(rows, [(UTC_1, 'true', 'PIN (1)', 'first pet', digest.hex(), fake_digest.hex(),
                                 'service_data.dek', '0', None, None, f'{USER_0}/{PREFERENCES}')])
        self.assertEqual(sources, [str(path)])

    def service_database(self, *rows, **database):
        path = self.extraction.database(**database)
        db = sqlite3.connect(path)
        db.execute('CREATE TABLE service (_id INTEGER PRIMARY KEY, protection_type INTEGER DEFAULT -1, '
                   'password_hash TEXT)')
        db.executemany('INSERT INTO service (protection_type, password_hash) VALUES (?, ?)', rows)
        db.commit()
        db.close()
        return path

    def test_service_table_is_reported_beside_the_preferences_not_in_place_of_them(self):
        database = self.service_database((1, 'old-hash'), dek=wrap(DATA_KEY), notes=[note()])
        current = base64.b64encode(bytes(range(20))).decode('ascii')
        preferences = self.extraction.preferences(strings={'password_hash': current},
                                                  typed={'protection_type': ('int', '2')})
        rows, sources = self.run_artifact(parser.private_notepad_settings)
        row = rows[0]
        self.assertEqual((row[2], row[4]), ('Pattern (2)', bytes(range(20)).hex()))
        self.assertEqual((row[8], row[9]), ('PIN (1)', 'old-hash'))
        self.assertEqual(sources, [str(preferences), str(database)])

    def test_service_hash_stays_as_stored_because_its_encoding_is_not_established(self):
        self.service_database((0, 'AAEC'))
        self.extraction.preferences()
        self.assertEqual(self.row()[9], 'AAEC')

    def test_empty_service_table_leaves_its_columns_blank(self):
        self.service_database(dek=wrap(DATA_KEY), notes=[note()])
        self.extraction.preferences(typed={'protection_type': ('int', '-1')})
        row = self.row()
        self.assertEqual((row[2], row[8], row[9]), ('Disabled (-1)', None, None))

    def test_service_values_give_a_row_without_preferences_or_a_data_key(self):
        database = self.service_database((1, 'old-hash'), notes=[note()])
        rows, sources = self.run_artifact(parser.private_notepad_settings)
        self.assertEqual(rows, [(None, None, None, None, None, None, '', '0', 'PIN (1)', 'old-hash',
                                 f'{USER_0}/{DATABASE}')])
        self.assertEqual(sources, [str(database)])

    def test_service_values_keep_a_row_when_the_preferences_do_not_parse(self):
        self.service_database((1, 'old-hash'))
        self.extraction.preferences(raw='<map><string')
        self.assertEqual(self.row()[8:10], ('PIN (1)', 'old-hash'))

    def test_only_the_first_service_row_is_read_as_the_app_reads_it(self):
        self.service_database((1, 'first'), (2, 'second'))
        self.extraction.preferences()
        self.assertEqual(self.row()[8:10], ('PIN (1)', 'first'))

    def test_protection_types_keep_the_stored_number(self):
        cases = {'-1': 'Disabled (-1)', '0': 'Password (0)', '1': 'PIN (1)', '2': 'Pattern (2)',
                 '9': 'Unknown (9)'}
        for stored, expected in cases.items():
            with self.subTest(stored=stored):
                self.setUp()
                self.extraction.preferences(typed={'protection_type': ('int', stored)})
                self.assertEqual(self.row()[2], expected)

    def test_absent_keys_are_blank_and_no_database_leaves_the_key_source_blank(self):
        self.extraction.preferences()
        self.assertEqual(self.row(), (None, None, None, None, None, None, '', '0', None, None,
                                      f'{USER_0}/{PREFERENCES}'))

    def test_values_that_do_not_convert_are_kept_as_stored(self):
        self.extraction.preferences(strings={'last_app_usage_time': 'soon', 'password_hash': 'a',
                                             'fake_password_hash': 'b'})
        row = self.row()
        self.assertEqual((row[0], row[4], row[5]), ('soon', 'a', 'b'))

    def test_database_without_preferences_gives_no_row(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note()])
        self.assertEqual(self.run_artifact(parser.private_notepad_settings), ([], []))

    def test_preferences_that_do_not_parse_give_no_row(self):
        self.extraction.preferences(raw='<map><string')
        self.assertEqual(self.run_artifact(parser.private_notepad_settings), ([], []))
        self.assertIn('unable to parse', self.logged())


class ContainersTest(PrivateNotepadCase):
    def test_each_android_user_is_read_with_its_own_key_and_preferences(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note(1, 'Owner')])
        self.extraction.preferences(typed={'protection_type': ('int', '1')})
        self.extraction.database(app=USER_10, notes=[note(1, 'Second user', key=OTHER_KEY)])
        self.extraction.preferences(app=USER_10, strings={'encryption_key': wrap(OTHER_KEY)},
                                    typed={'protection_type': ('int', '2')})

        rows, _ = self.run_artifact(parser.private_notepad_notes)
        self.assertEqual([(r[3], r[7]) for r in rows], [('Owner', f'{USER_0}/{DATABASE}'),
                                                        ('Second user', f'{USER_10}/{DATABASE}')])
        rows, _ = self.run_artifact(parser.private_notepad_settings)
        self.assertEqual([(r[2], r[6], r[7]) for r in rows], [
            ('PIN (1)', 'service_data.dek', '0'),
            ('Pattern (2)', 'encryption_key preference', '10')])

    def test_storage_views_of_one_app_folder_are_read_once(self):
        views = (USER_0, f'data/user/0/{PACKAGE}', f'data_mirror/data_ce/null/0/{PACKAGE}')
        for view in views:
            self.extraction.database(app=view, dek=wrap(DATA_KEY), notes=[note()])
            self.extraction.preferences(app=view)
        rows, _ = self.run_artifact(parser.private_notepad_notes)
        self.assertEqual([r[7] for r in rows], [f'{USER_0}/{DATABASE}'])
        rows, _ = self.run_artifact(parser.private_notepad_settings)
        self.assertEqual([r[-1] for r in rows], [f'{USER_0}/{PREFERENCES}'])

    def test_files_outside_the_app_folder_are_ignored(self):
        self.extraction.add('elsewhere/databases/notes.db', b'not this app')
        self.assertEqual(parser.get_containers(self.extraction.context()), [])

    def test_a_file_that_is_no_database_gives_no_rows(self):
        self.extraction.add(f'{USER_0}/{DATABASE}', b'this is not an SQLite database' * 10)
        self.assertEqual(self.run_artifact(parser.private_notepad_notes)[0], [])
        self.assertEqual(self.run_artifact(parser.private_notepad_passwords)[0], [])
        self.assertEqual(self.run_artifact(parser.private_notepad_attachments)[0], [])

    def test_no_artifact_alters_the_evidence(self):
        self.extraction.database(dek=wrap(DATA_KEY), notes=[note(images=ids('img'))], passwords=[
            {'_id': 1, 'password_name': text('Bank')}])
        self.extraction.preferences(strings={'encryption_key': wrap(DATA_KEY)})
        self.extraction.attachment('img')

        def state():
            return {path.relative_to(self.extraction.root).as_posix():
                    hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in self.extraction.root.rglob('*') if path.is_file()}

        before = state()
        for artifact in (parser.private_notepad_notes, parser.private_notepad_attachments,
                         parser.private_notepad_passwords, parser.private_notepad_settings):
            self.run_artifact(artifact)
        self.assertEqual(state(), before)


class IntruderPathsTest(unittest.TestCase):
    def test_only_the_intruder_artifact_matches_its_folder_and_it_matches_nothing_else(self):
        for artifact in parser.__artifacts_v2__:
            matched = any(fnmatch.fnmatchcase(f'root/{INTRUDER}/1.jpg', pattern)
                          for pattern in parser.__artifacts_v2__[artifact]['paths'])
            self.assertEqual(matched, artifact == 'private_notepad_intruder_photos', artifact)
        patterns = parser.__artifacts_v2__['private_notepad_intruder_photos']['paths']
        self.assertFalse(any(fnmatch.fnmatchcase(f'root/{USER_0}/{DATABASE}', pattern)
                             for pattern in patterns))


class MetadataTest(unittest.TestCase):
    @staticmethod
    def matches(artifact, relative):
        # The seekers prepend root/ before matching, so a leading */ can match
        patterns = parser.__artifacts_v2__[artifact]['paths']
        return any(fnmatch.fnmatchcase(f'root/{relative}', pattern) for pattern in patterns)

    def test_block_is_a_literal_so_the_repo_checkers_can_read_it(self):
        source = pathlib.Path(parser.__file__).read_text(encoding='utf-8')
        block = next(node.value for node in ast.parse(source).body
                     if isinstance(node, ast.Assign) and node.targets[0].id == '__artifacts_v2__')
        self.assertEqual(ast.literal_eval(block), parser.__artifacts_v2__)

    def test_every_artifact_matches_its_database_and_preferences_in_every_storage_view(self):
        views = (USER_0, USER_10, f'data/user/0/{PACKAGE}', f'userdata/data/{PACKAGE}',
                 f'data_mirror/data_ce/null/0/{PACKAGE}')
        for artifact in set(parser.__artifacts_v2__) - {'private_notepad_intruder_photos'}:
            for view in views:
                for path in (DATABASE, f'{DATABASE}-wal', PREFERENCES):
                    with self.subTest(artifact=artifact, view=view, path=path):
                        self.assertTrue(self.matches(artifact, f'{view}/{path}'))

    def test_only_the_artifacts_that_read_attachments_match_them(self):
        for app in (USER_0, USER_10):
            for folder in ('images', 'recordings'):
                path = f'{app}/files/{folder}/1700000000000'
                self.assertTrue(self.matches('private_notepad_notes', path))
                self.assertTrue(self.matches('private_notepad_attachments', path))
                self.assertFalse(self.matches('private_notepad_passwords', path))
                self.assertFalse(self.matches('private_notepad_settings', path))

    def test_no_artifact_matches_the_rest_of_the_app_folder(self):
        for path in ('cache/WebView/index', 'files/credentials.dat', 'files/image_previews/1',
                     'databases/google_app_measurement_local.db',
                     'shared_prefs/com.google.firebase.abt.xml', 'no_backup/a'):
            for artifact in parser.__artifacts_v2__:
                with self.subTest(artifact=artifact, path=path):
                    self.assertFalse(self.matches(artifact, f'{USER_0}/{path}'))


if __name__ == '__main__':
    unittest.main()
