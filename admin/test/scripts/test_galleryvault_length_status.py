"""Length observations must not imply content verification."""
import json
import struct
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from Crypto.Cipher import DES
from scripts.artifacts import galleryVault


def wrap(data):
    size = 8 - len(data) % 8
    return DES.new(b'tianxiaw', DES.MODE_ECB).encrypt(data + bytes([size]) * size)


def object_bytes(plain, size, key=b'abcd', check=0):
    block = min(4, len(plain))
    head = bytes(x ^ key[i % len(key)] ^ i for i, x in enumerate(plain[:block])) if key else b''
    wrapped = wrap(key)
    metadata = wrap(json.dumps({'name': 'sample.png', 'uuid': 'fixture'}).encode())
    return (b'X' * block + plain[block:] + b'>>tyfs>>' + head
            + struct.pack('>QQB', block, size, check) + wrapped
            + struct.pack('>Q', len(wrapped)) + metadata
            + struct.pack('>Q', len(metadata)) + b'\x00\x01<<tyfs<<')


class TestGalleryVaultLengthStatus(unittest.TestCase):
    def test_declared_bytes_cap_short_zero_and_unused_check(self):
        plain = b'\x89PNG\r\n\x1a\n' + b'known payload'
        cases = [(len(plain), b'abcd', 0), (len(plain), b'abcd', 255),
                 (len(plain) + 9, b'abcd', 0), (len(plain) - 3, b'abcd', 0),
                 (0, b'abcd', 0), (9, b'', 0)]
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for i, (size, key, check) in enumerate(cases):
                path = Path(tmp) / str(i)
                path.write_bytes(object_bytes(plain if key else b'', size, key, check))
                paths.append(path)
            paths.append(paths[0])
            context = SimpleNamespace(get_files_found=lambda: paths,
                                      get_relative_path=lambda p: Path(p).name)
            captured = []
            with patch.object(galleryVault, 'check_in_embedded_media',
                              side_effect=lambda source, data, name, **kw:
                              captured.append(data) or 'media'):
                headers, rows, _ = galleryVault.galleryvault_vault_files.__wrapped__(context)
            self.assertEqual(len(headers), 11)
            self.assertEqual(len(rows), 7)
            self.assertEqual(captured, [plain, plain, plain, plain[:-3], plain])
            self.assertEqual(rows[0][3], rows[1][3])
            self.assertIn('equals stored size', rows[0][3])
            self.assertIn('capped to stored size; content not verified', rows[3][3])
            self.assertIn('of ' + str(len(plain) + 9) + ' bytes', rows[2][3])
            self.assertEqual([r[3] for r in rows[4:6]], ['No nonempty rebuilt bytes'] * 2)
            self.assertEqual(rows[0], rows[-1])
