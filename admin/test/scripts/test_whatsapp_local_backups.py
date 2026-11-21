"""WhatsApp - Local Backups: header and key file readers, storage spellings and key matching, on constructed files."""
import hashlib
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.artifacts import whatsAppLocalBackups as wa


def varint(value):
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def field(number, value):
    """One protobuf field: an int as a varint, bytes or str as length-delimited."""
    if isinstance(value, int):
        return varint(number << 3) + varint(value)
    data = value.encode() if isinstance(value, str) else value
    return varint((number << 3) | 2) + varint(len(data)) + data


SERVER = bytes(range(32))
GOOGLE = bytes(range(100, 116))


def crypt14(key_type_new=0, deprecated=0, version='2.26.44.90', suffix='42', backup_version=1, cleaned=1,
            server=SERVER, google=GOOGLE, padding=b'\x00' * 64):
    c14 = field(1, b'\x00\x01') + field(2, b'2') + field(3, server) + field(4, google) + field(5, b'\x11' * 16)
    meta = field(1, version) + field(3, suffix) + field(4, backup_version) + field(5, 1) + field(39, cleaned)
    prefix = field(1, deprecated) + field(2, c14) + field(4, meta)
    if key_type_new is not None:
        prefix += field(6, key_type_new)
    return varint(len(prefix)) + prefix + padding


def crypt15():
    meta = field(1, '2.26.44.90') + field(3, '42')
    prefix = field(1, 1) + field(3, field(1, b'\x22' * 16)) + field(4, meta) + field(6, 3)
    return varint(len(prefix)) + prefix + b'\x00' * 32


def crypt12(server=SERVER, google=GOOGLE):
    return b'\x00\x01' + b'\x02' + server + google + b'\x33' * 16 + b'\x00' * 64


def key_file(server=SERVER, google=GOOGLE, digest=None):
    array = b'\x00\x01' + b'\x02' + server + google + (digest or hashlib.sha256(google).digest()) + b'\x00' * 16 + b'\x44' * 32
    return (b'\xac\xed\x00\x05\x75\x72\x00\x02\x5b\x42' + b'\xac\xf3\x17\xf8\x06\x08\x54\xe0' + b'\x02\x00\x00\x78\x70'
            + len(array).to_bytes(4, 'big') + array)


class HeaderTests(unittest.TestCase):
    def test_crypt14_fields(self):
        header = wa.parse_header(crypt14(key_type_new=0, deprecated=0))
        self.assertEqual(header['format'], 'crypt14')
        self.assertEqual(header['key_type'], 0)
        self.assertEqual(header['key_type_field'], '6')
        self.assertEqual(header['app_version'], '2.26.44.90')
        self.assertEqual(header['jid_suffix'], '42')
        self.assertEqual(header['backup_version'], 1)
        self.assertEqual(header['cleaned_db'], 1)
        self.assertEqual(header['server_salt'], SERVER)
        self.assertEqual(header['google_id_salt'], GOOGLE)

    def test_the_deprecated_key_type_when_the_new_one_is_absent(self):
        header = wa.parse_header(crypt14(key_type_new=None, deprecated=0))
        self.assertEqual(header['key_type'], 0)
        self.assertEqual(header['key_type_field'], '1')

    def test_crypt15_has_no_salts(self):
        header = wa.parse_header(crypt15())
        self.assertEqual(header['format'], 'crypt15')
        self.assertEqual(header['key_type'], 3)
        self.assertEqual(header['server_salt'], b'')

    def test_a_header_size_needing_two_varint_bytes(self):
        header = wa.parse_header(crypt14(version='2.26.' + '9' * 140))
        self.assertEqual(header['format'], 'crypt14')
        self.assertGreater(header['header_size'], 130)

    def test_crypt12(self):
        header = wa.parse_header(crypt12())
        self.assertEqual(header['format'], 'crypt12')
        self.assertEqual(header['header_size'], 67)
        self.assertEqual(header['server_salt'], SERVER)

    def test_other_files_are_not_recognised(self):
        self.assertIsNone(wa.parse_header(b'SQLite format 3\x00' + b'\x00' * 100))
        self.assertIsNone(wa.parse_header(b'\xff' * 100))
        self.assertIsNone(wa.parse_header(b''))


class KeyFileTests(unittest.TestCase):
    def test_salts_of_a_key_file(self):
        self.assertEqual(wa.parse_key_file(key_file()), (SERVER, GOOGLE))

    def test_refusals(self):
        self.assertIsNone(wa.parse_key_file(b'\x00' + key_file()[1:]))
        self.assertIsNone(wa.parse_key_file(key_file(digest=b'\x00' * 32)))
        self.assertIsNone(wa.parse_key_file(key_file()[:60]))
        self.assertIsNone(wa.parse_key_file(b''))


class StorageTests(unittest.TestCase):
    def test_storage_users(self):
        tail = 'Android/media/com.whatsapp/WhatsApp/Databases/msgstore.db.crypt14'
        for path, user in (('data/media/0/' + tail, '0'), ('Dump/data/media/10/' + tail, '10'),
                           ('userdata/media/0/' + tail, '0'), ('Dump/mnt/pass_through/10/emulated/0/' + tail, '0'),
                           ('mnt/user/0/emulated/11/' + tail, '11'), ('storage/emulated/0/' + tail, '0'),
                           ('sdcard/' + tail, '')):
            self.assertEqual(wa.storage_key(path)[0], user, path)
        self.assertEqual(wa.storage_key('data/media/0/' + tail)[1], tail)


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = [str(path) for path in files]

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace(os.sep, '/')

    @staticmethod
    def get_seeker():
        return None


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.work)

    def put(self, relative, data):
        path = self.work / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def test_rows_copies_and_key_matches(self):
        db = 'Android/media/com.whatsapp/WhatsApp/Databases/msgstore.db.crypt14'
        files = [
            self.put('data/media/0/' + db, crypt14()),
            self.put('Dump/mnt/pass_through/10/emulated/0/' + db, crypt14()),
            self.put('data/media/10/' + db, crypt14(server=b'\x55' * 32)),
            self.put('data/media/0/Android/media/com.whatsapp/WhatsApp/Backups/wa.db.crypt14', crypt14()),
            self.put('data/media/0/WhatsApp Business/Databases/msgstore.db.crypt12', crypt12()),
            self.put('data/media/0/WhatsApp/Databases/broken.db.crypt14', b'\xff' * 80),
            self.put('data/data/com.whatsapp/files/key', key_file()),
            self.put('data/user/0/com.whatsapp/files/key', key_file()),
            self.put('data/data/com.example.decoy/files/key', key_file(server=b'\x55' * 32)),
        ]
        (self.work / 'data/media/0/Android/media/com.whatsapp/WhatsApp/Backups/Stickers.crypt14').mkdir()
        files.append(self.work / 'data/media/0/Android/media/com.whatsapp/WhatsApp/Backups/Stickers.crypt14')
        headers, rows, source = wa.whatsapp_local_backups.__wrapped__(Context(self.work, files))
        self.assertEqual(len(headers), len(rows[0]))
        index = {name: position for position, name in enumerate(h if isinstance(h, str) else h[0] for h in headers)}
        found = {(row[index['App']], row[index['Storage User']], row[index['Backup Of']]): row for row in rows}
        self.assertEqual(len(rows), 5)
        user0 = found[('WhatsApp', '0', 'msgstore.db')]
        self.assertEqual(user0[index['Copies']], 2)
        self.assertEqual(user0[index['Source File']], 'data/media/0/' + db)
        self.assertEqual(user0[index['Matching Key File']], 'data/data/com.whatsapp/files/key')
        self.assertEqual(user0[index['Key Type (as stored)']], 'WA_PROVIDED (0)')
        self.assertEqual(found[('WhatsApp', '10', 'msgstore.db')][index['Matching Key File']], '')
        business = found[('WhatsApp Business', '0', 'msgstore.db')]
        self.assertEqual(business[index['Format']], 'crypt12')
        self.assertEqual(business[index['Key Type (as stored)']], '')
        self.assertEqual(found[('WhatsApp', '0', 'broken.db')][index['Format']], 'not recognised')
        self.assertIn(str(self.work / 'data/data/com.whatsapp/files/key'), source.split('\n'))


if __name__ == '__main__':
    unittest.main()
