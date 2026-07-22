"""NQ Vault path security tests.

Historically NQ_Vault.file_decryption wrote decrypted media into the report
folder using the attacker-controlled original filename from the vault DB,
guarded by sanitize_output_filename/build_safe_output_path. The LAVA
conversion (f5f5025) replaced that write path with check_in_embedded_media,
which stores media under a sha1-based filename - so path traversal via the
output path is structurally impossible. The remaining attacker-controlled
input is the display/check-in name (the media store derives a file suffix
from it), so these tests verify that name is sanitized and that processing
a hostile vault DB entry never writes outside the report folder.
"""
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
import uuid


ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.artifacts import NQ_Vault


class TestNQVaultPathSecurity(unittest.TestCase):
    def test_sanitize_output_filename_removes_traversal(self):
        sanitized = NQ_Vault.sanitize_output_filename('../../../Users/examiner/.zshrc')
        self.assertEqual(sanitized, 'zshrc')

    def test_sanitize_output_filename_handles_hostile_names(self):
        # Windows-style traversal
        self.assertEqual(NQ_Vault.sanitize_output_filename('..\\..\\evil.bin'), 'evil.bin')
        # Names that reduce to nothing fall back to the default
        self.assertEqual(NQ_Vault.sanitize_output_filename(''), 'recovered_file.bin')
        self.assertEqual(NQ_Vault.sanitize_output_filename(None), 'recovered_file.bin')
        self.assertEqual(NQ_Vault.sanitize_output_filename('...'), 'recovered_file.bin')
        self.assertEqual(
            NQ_Vault.sanitize_output_filename('.', default_name='1700000000.bin'),
            '1700000000.bin')
        # Path separators and reserved characters are neutralized, so the media
        # store's suffix derivation (name.split('.')[-1]) cannot see a separator
        self.assertEqual(NQ_Vault.sanitize_output_filename('x.a/b'), 'b')
        self.assertNotIn('/', NQ_Vault.sanitize_output_filename('bad<name>?.a*b'))

    def test_media_pipeline_blocks_path_traversal_write(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            report_folder = base / 'report'
            report_folder.mkdir()

            # Encrypted media file: NQ Vault XORs the first 128 bytes.
            # password_id hash '1477632' -> PIN 0 -> XOR key 0x30.
            image_dir = base / 'payload' / '.image'
            image_dir.mkdir(parents=True)
            plaintext = b'A' * 200
            encrypted = bytes((b ^ 0x30) if i < 128 else b for i, b in enumerate(plaintext))
            encrypted_file = image_dir / '1700000000.bin'
            encrypted_file.write_bytes(encrypted)

            unique_name = f'outside_written_{uuid.uuid4().hex}.bin'
            traversal_name = f'../../../{unique_name}'

            # Vault DB with an attacker-controlled original filename
            db_path = base / '322w465ay423xy11'
            connection = sqlite3.connect(db_path)
            connection.executescript('''
                CREATE TABLE hideimagevideo (file_path_from TEXT, file_name_from TEXT,
                    file_path_new TEXT, [time] INTEGER, [viode_time] INTEGER,
                    resolution TEXT, album_id INTEGER, password_id TEXT);
                CREATE TABLE albums (_id INTEGER, album_name TEXT);
                CREATE TABLE albumstemp (album_temp_id INTEGER, album_name_temp TEXT);
                INSERT INTO albums VALUES (1, 'Default');
            ''')
            connection.execute(
                'INSERT INTO hideimagevideo VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                ('/sdcard/DCIM/Camera/original.jpg', traversal_name,
                 '/sdcard/SystemAndroid/Data/hash/.image/1700000000.bin',
                 1700000000000, 0, '', 1, '1477632'))
            connection.commit()
            connection.close()

            files_found = [str(db_path), str(encrypted_file)]

            # Stub the media store so the artifact runs without the full LAVA
            # context; capture the name the artifact checks media in under.
            checked_in = []

            def fake_check_in_embedded_media(source_file, data, name='', **kwargs):
                checked_in.append({'source': source_file, 'data': data, 'name': name})
                return 'media-ref'

            original_check_in = NQ_Vault.check_in_embedded_media
            NQ_Vault.check_in_embedded_media = fake_check_in_embedded_media
            self.addCleanup(setattr, NQ_Vault, 'check_in_embedded_media', original_check_in)

            class FakeContext:
                @staticmethod
                def get_files_found():
                    return files_found

                @staticmethod
                def get_relative_path(path):
                    return str(path)

            _, data_list, _ = NQ_Vault.get_NQVault_media.__wrapped__(FakeContext)

            # The decryption ran and produced exactly one media check-in
            self.assertEqual(len(data_list), 1)
            self.assertEqual(len(checked_in), 1)
            self.assertEqual(checked_in[0]['data'], plaintext)

            # The check-in name is sanitized: no traversal, no separators
            self.assertEqual(checked_in[0]['name'], unique_name)
            self.assertNotIn('..', checked_in[0]['name'])
            self.assertNotIn('/', checked_in[0]['name'])
            self.assertNotIn('\\', checked_in[0]['name'])

            # Nothing was written outside the report folder
            outside_target = (report_folder / traversal_name).resolve()
            self.assertFalse(outside_target.exists())
            self.assertFalse((base / unique_name).exists())


if __name__ == '__main__':
    unittest.main()
