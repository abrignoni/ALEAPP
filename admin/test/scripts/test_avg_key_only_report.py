"""Known constructed crypto proves both key-output paths without exhaustive search."""
import ast
import base64
from binascii import unhexlify
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
import xml.etree.ElementTree as ET
from Crypto.Cipher import AES
from Crypto.Hash import SHA1
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad
from scripts.artifacts import AVG as avg
from admin.test.scripts.test_history_doclist_all_sources import Context

MASTER = bytes(range(32))
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aEbcAAAAASUVORK5CYII=')


def create_avg_fixture(root, settings=False, media=False, master=MASTER, image=PNG):
    root = Path(root)
    tree = ast.parse(Path(avg.__file__).read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_compute_avg')
    encoded = next(ast.literal_eval(n.value) for n in ast.walk(function)
                   if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'pinFile'
                                                       for t in n.targets))
    pin, java_pin = base64.b64decode(encoded).split(b'\n')[:2]
    iv = bytes(range(16))
    derived = PBKDF2(unhexlify(java_pin), iv, 16, count=100, hmac_hash_module=SHA1)
    encrypted = AES.new(derived, AES.MODE_CBC, iv).encrypt(hashlib.sha256(master).digest()+master)
    key = root/'data/data/com.antivirus/Vault/.key_store/key'
    key.parent.mkdir(parents=True, exist_ok=True)
    key.write_bytes(b'\0'*8+iv+encrypted)
    files = [str(key)]
    if settings:
        path = root/'data/data/com.antivirus/shared_prefs/PinSettingsImpl.xml'
        path.parent.mkdir(parents=True, exist_ok=True)
        xml = ET.Element('map')
        ET.SubElement(xml, 'string', name='encrypted_pin').text = hashlib.sha1(pin).hexdigest()
        ET.ElementTree(xml).write(path)
        files.append(str(path))
    if media:
        image_path = root/'data/data/com.antivirus/Vault/pictures/encrypted-picture'
        image_path.parent.mkdir(parents=True, exist_ok=True)
        ciphertext = AES.new(master, AES.MODE_CBC, iv).encrypt(pad(image,16))
        image_path.write_bytes(struct.pack('>I',16)+iv+struct.pack('>I',len(ciphertext))+ciphertext)
        files.append(str(image_path))
    return files


class TestAvgKeyOnlyReport(unittest.TestCase):
    def test_key_only_and_settings_identified_key_values(self):
        for settings in [False, True]:
            with self.subTest(settings=settings), tempfile.TemporaryDirectory() as directory:
                files = create_avg_fixture(directory, settings=settings)
                _, rows, _ = avg.get_AVG.__wrapped__(Context(directory, files))
                self.assertEqual([row[1] for row in rows if row[0]=='Master Key'], [MASTER.hex()])
                self.assertIn('Derived Key', [row[0] for row in rows])
                self.assertNotIn('Java Equivilant', [row[0] for row in rows])
                self.assertIn('Java Equivalent', [row[0] for row in rows])
                self.assertEqual(len(rows), 9 if settings else 7)

    def test_no_key_does_not_fabricate_key_output(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(avg.get_AVG.__wrapped__(Context(directory, []))[1], [])
