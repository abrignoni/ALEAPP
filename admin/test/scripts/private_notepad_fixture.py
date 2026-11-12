"""Builds synthetic Private Notepad (ru.alexandermalikov.protectednotes) app data.

Every value is invented. The files are made by running the app's encryption chain in reverse: a data key
is wrapped under the static key, and text and attachment files are encrypted under the data key. The
schema is the one scripts/artifacts/privateNotepad.py queries, not one observed on a device, so data
built here proves the parser handles this scheme and says nothing about what an installed app writes.

The static key is held here as a known answer and the encryption is done here, independently of the
parser. Taking the key from the parser's get_static_key() would let a wrong key pass, since both sides
would then agree on it.

test_private_notepad.py builds its cases with Extraction. Run as a script, this module writes one
persistent extraction that exercises every artifact, for a run of ALEAPP over a folder (-t fs):

    python admin/test/scripts/private_notepad_fixture.py <output folder>

The output folder must be empty or not exist yet.
"""
import base64
import json
import pathlib
import sqlite3
import sys
from xml.sax.saxutils import escape, quoteattr

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

PACKAGE = 'ru.alexandermalikov.protectednotes'
USER_0 = f'data/data/{PACKAGE}'
USER_10 = f'data/user/10/{PACKAGE}'
USER_11 = f'data/user/11/{PACKAGE}'
DATABASE = 'databases/notes.db'
PREFERENCES = 'shared_prefs/protected_notes_preferences.xml'
INTRUDER = f'{USER_0}/files/intruder_photos'

STATIC_KEY = bytes.fromhex('e16245b64c30509a931ddf9d24db406b')
DATA_KEY = bytes(range(16))
OTHER_KEY = bytes(range(16, 32))
ZERO_IV = b'\x00' * 16

PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')
MP3 = b'ID3\x03\x00\x00\x00\x00\x00\x00' + b'\x00' * 32
JPEG = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00' + b'\x00' * 32

NOTE_COLUMNS = ('_id', 'date', 'date_created', 'date_delete', 'title', 'note', 'images',
                'audio_files')
PASSWORD_COLUMNS = ('_id', 'date_created', 'password_name', 'password_login', 'password_password',
                    'password_site_address', 'password_comment')

MS_1 = 1700000000000  # 2023-11-14 22:13:20 UTC
MS_2 = 1600000000123  # 2020-09-13 12:26:40.123 UTC


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
    """A folder holding the app's files at the paths an extraction would."""

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

    def database(self, app=USER_0, notes=(), passwords=None, dek=None, service=None,
                 note_columns=NOTE_COLUMNS):
        """notes.db; a table whose argument is None is left out, and service holds
        (protection_type, password_hash) rows."""
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
            if service is not None:
                db.execute('CREATE TABLE service (_id INTEGER PRIMARY KEY, '
                           'protection_type INTEGER DEFAULT -1, password_hash TEXT)')
                db.executemany('INSERT INTO service (protection_type, password_hash) VALUES (?, ?)',
                               service)
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


def build_dump(root):
    """One extraction exercising every artifact; returns the Extraction."""
    extraction = Extraction(root)
    hash_ = base64.b64encode(bytes(range(20))).decode('ascii')
    fake_hash = base64.b64encode(bytes(range(20, 40))).decode('ascii')

    # Android user 0: data key in service_data.dek and in the preferences
    extraction.database(
        dek=wrap(DATA_KEY),
        notes=[
            note(1, 'Indkøb æøå', 'Mælk, brød, æg', date=MS_1, date_created=MS_2, date_delete=0,
                 images=ids('img-1'), audio_files=ids('aud-1', name='audio_ids')),
            note(2, 'Тайная заметка', '日本語のメモ', date=MS_2, date_created=MS_2),
            {'_id': 3, 'date': MS_1, 'title': text('Readable title'),
             'note': text('Body under another key', OTHER_KEY)},
            note(4, 'Missing attachment', 'Names a file that is not there', date=MS_1,
                 images=ids('gone')),
        ],
        passwords=[{
            '_id': 1, 'date_created': MS_1, 'password_name': text('Bank'),
            'password_login': text('user@example.invalid'), 'password_password': text('hunter2'),
            'password_site_address': text('https://example.invalid'),
            'password_comment': text('Kommentar æøå')}],
        service=[(1, 'old-hash')])
    extraction.preferences(
        strings={'encryption_key': wrap(DATA_KEY), 'password_hint': 'first pet',
                 'password_hash': hash_, 'fake_password_hash': fake_hash},
        typed={'protection_type': ('int', '1'), 'last_app_usage_time': ('long', str(MS_1)),
               'show_lock_screen': ('boolean', 'true')})
    extraction.attachment('img-1', PNG)
    extraction.attachment('aud-1', MP3, folder='recordings')
    extraction.attachment('orphan', PNG)
    extraction.attachment('another-key', PNG, key=OTHER_KEY)
    extraction.add(f'{INTRUDER}/{MS_1}.jpg', JPEG)

    # Android user 10: its own data key, in the preferences only
    extraction.database(app=USER_10, notes=[note(1, 'Second user', 'Body', key=OTHER_KEY,
                                                 date=MS_2)])
    extraction.preferences(app=USER_10, strings={'encryption_key': wrap(OTHER_KEY)},
                           typed={'protection_type': ('int', '2')})

    # Android user 11: the first stored field is damaged, so the key is confirmed on the others
    damaged = base64.b64encode(b'not ciphertext!!').decode('ascii')
    extraction.database(app=USER_11, dek=wrap(DATA_KEY), notes=[
        {'_id': 1, 'date': MS_1, 'title': damaged, 'note': text('Body after a damaged title')},
        note(2, 'Intact note', 'Body', date=MS_2)])
    extraction.preferences(app=USER_11)
    return extraction


def main(output):
    root = pathlib.Path(output)
    if root.exists() and any(root.iterdir()):
        sys.exit(f'{root} is not empty; give an empty or new folder')
    extraction = build_dump(root)
    print(f'Data key, users 0 and 11: {DATA_KEY.hex()}')
    print(f'Data key, user 10: {OTHER_KEY.hex()}')
    for path in extraction.files:
        print(path.relative_to(root).as_posix(), path.stat().st_size)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'private_notepad_fixture_out')
