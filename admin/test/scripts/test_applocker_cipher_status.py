"""Cipher completion and signature recognition are independent observations."""
import base64
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from Crypto.Cipher import AES  # pylint: disable=wrong-import-position
from scripts.artifacts.appLockerfishingnet import (  # pylint: disable=wrong-import-position
    STANDARD_KEY, STANDARD_IV, get_appLockerfishingnet,
)

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')


def make_fixture(root):
    """Use actual CBC bytes; padding remains present in the expected output."""
    root = pathlib.Path(root)
    padded = PNG + bytes([16 - len(PNG) % 16]) * (16 - len(PNG) % 16)
    unknown = b'Unrecognized CBC output bytes!!!'
    assert len(unknown) % 16 == 0
    cipher = lambda data: AES.new(bytes.fromhex(STANDARD_KEY), AES.MODE_CBC,
                                  bytes.fromhex(STANDARD_IV)).encrypt(data)
    payloads = {'recognized': PNG, 'cipher-png': cipher(padded),
                'cipher-unknown': cipher(unknown), 'invalid-length': b'abc',
                'empty': b'', '~ignored': b'abc', '._ignored': b'abc'}
    paths = []
    for name, data in payloads.items():
        path = root / 'data/media/0/.privacy_safe/picture' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        paths.append(path)
    return paths, {'cipher-png': padded, 'cipher-unknown': unknown}


class AppLockerCipherStatusTest(unittest.TestCase):
    def test_actual_cipher_bytes_outcome_and_mime_are_separate(self):
        with tempfile.TemporaryDirectory() as folder:
            paths, expected = make_fixture(folder)
            context = SimpleNamespace(get_files_found=lambda: paths,
                                      get_relative_path=lambda p: str(pathlib.Path(p).relative_to(folder)))
            with patch('scripts.artifacts.appLockerfishingnet.check_in_media',
                       side_effect=lambda p, n: 'input:' + n) as original, \
                 patch('scripts.artifacts.appLockerfishingnet.check_in_embedded_media',
                       side_effect=lambda p, d, n, **kwargs: 'output:' + n) as embedded, \
                 patch('scripts.artifacts.appLockerfishingnet.logfunc') as log:
                headers, rows, source = get_appLockerfishingnet.__wrapped__(context)
            self.assertEqual(headers, (('Media', 'media'), 'Filename', 'Cipher Operation',
                                       'Recognized Output Type', 'Full Path'))
            self.assertEqual(len(rows), 4)
            self.assertEqual([r[2] for r in rows], ['Not attempted (recognized input)',
                             'Completed (output not authenticated)',
                             'Completed (output not authenticated)', 'Failed'])
            self.assertEqual([r[3] for r in rows], ['', 'image/png', '', ''])
            self.assertEqual([r[1] for r in rows], [p.name for p in paths[:4]])
            self.assertEqual([r[4] for r in rows], [str(p.relative_to(folder)) for p in paths[:4]])
            self.assertEqual(source, 'data/media/0/.privacy_safe')
            self.assertEqual([c.args[1] for c in original.call_args_list], ['recognized', 'invalid-length'])
            self.assertEqual(embedded.call_args_list[0].args[1:], (expected['cipher-png'], 'cipher-png.png'))
            self.assertEqual(embedded.call_args_list[0].kwargs,
                             {'force_type': 'image/png', 'force_extension': 'png'})
            self.assertEqual(embedded.call_args_list[1].args[1:], (expected['cipher-unknown'], 'cipher-unknown'))
            self.assertEqual(embedded.call_args_list[1].kwargs, {})
            self.assertEqual(log.call_count, 1)
            self.assertIn('Cipher operation failed', log.call_args.args[0])

    def test_video_directory_and_repeated_files_keep_selection_order(self):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / '.privacy_safe/video/item'
            path.parent.mkdir(parents=True)
            path.write_bytes(PNG)
            context = SimpleNamespace(get_files_found=lambda: [path, path, path.parent],
                                      get_relative_path=lambda p: str(pathlib.Path(p).relative_to(folder)))
            with patch('scripts.artifacts.appLockerfishingnet.check_in_media', return_value='media'):
                _, rows, _ = get_appLockerfishingnet.__wrapped__(context)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0], rows[1])
