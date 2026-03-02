import os
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
import scripts.ilapfuncs as ilapfuncs


class TestNQVaultPathSecurity(unittest.TestCase):
    def test_sanitize_output_filename_removes_traversal(self):
        sanitized = NQ_Vault._sanitize_output_filename('../../../Users/examiner/.zshrc')
        self.assertEqual(sanitized, 'zshrc')

    def test_build_safe_output_path_is_confined_to_report_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            report_folder = Path(tmpdir) / 'report'
            report_folder.mkdir()
            safe_path = NQ_Vault._build_safe_output_path(
                str(report_folder),
                '../../../../../../outside_written.bin',
            )
            self.assertTrue(str(safe_path).startswith(str(report_folder.resolve())))
            self.assertEqual(safe_path.name, 'outside_written.bin')

    def test_file_decryption_blocks_path_traversal_write(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            report_folder = base / 'report'
            report_folder.mkdir()
            ilapfuncs.OutputParameters.screen_output_file_path = str(base / 'screen_output.html')

            image_dir = base / 'payload' / '.image'
            image_dir.mkdir(parents=True)
            encrypted_file = image_dir / '1700000000.bin'
            encrypted_file.write_bytes(b'A' * 200)

            unique_name = f'outside_written_{uuid.uuid4().hex}.bin'
            traversal_name = f'../../../{unique_name}'
            file_info = {
                '1700000000.bin': {
                    'old_filepath': '/sdcard/DCIM/Camera/original.jpg',
                    'old_filename': traversal_name,
                    'vault_filepath': '/sdcard/SystemAndroid/Data/hash/.image/1700000000.bin',
                    'timestamp': '2024-01-01 00:00:00',
                    'vid_length': '',
                    'resolution': '',
                    'alb_name': 'Default',
                    'prev_alb_name': '',
                    'password_id': 'enc-pin-id',
                }
            }
            pin_info = {
                'enc-pin-id': {
                    'xor_key': '0x00',
                    'pin_for_XOR_key': '0000',
                }
            }

            NQ_Vault.file_decryption([str(encrypted_file)], file_info, pin_info, str(report_folder))

            outside_target = (report_folder / traversal_name).resolve()
            self.assertFalse(outside_target.exists())
            self.assertTrue((report_folder / unique_name).exists())


if __name__ == '__main__':
    unittest.main()
