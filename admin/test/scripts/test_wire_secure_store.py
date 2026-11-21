"""Wire secure-store key handling: Tink keyset parsing, EncryptedSharedPreferences decryption
(PyCryptodome decrypting vectors produced by a second library), associated-data binding, and the
database-secret derivation. The ciphertext vectors below were produced with the `cryptography`
library's AES-SIV and AES-GCM, so a passing decrypt proves the module's PyCryptodome port agrees
with an independent implementation."""
import base64
import json
import pathlib
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import wireMessenger as wire  # pylint: disable=wrong-import-position

# Tink keysets. KS_KEYS holds two keys whose primary is the SECOND entry, so a reader that took
# the first key would get the wrong (decoy) material and fail.
KS_KEYS = ('CIfkBhKDAQp6CjB0eXBlLmdvb2dsZWFwaXMuY29tL2dvb2dsZS5jcnlwdG8udGluay5BZXNTaXZLZXkSRAgAEk'
           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
           'GAMQARjnByABEoQBCnoKMHR5cGUuZ29vZ2xlYXBpcy5jb20vZ29vZ2xlLmNyeXB0by50aW5rLkFlc1NpdktleR'
           'JECAASQAABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6'
           'Ozw9Pj8YAxABGIfkBiAB')
KS_VALS = ('CI7IDRJkCloKMHR5cGUuZ29vZ2xlYXBpcy5jb20vZ29vZ2xlLmNyeXB0by50aW5rLkFlc0djbUtleRIkCAAaIC'
           'AhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/GAMQARiOyA0gAQ==')
ENC_NAME = 'AQABsgd4hHwq9GKpsXI3YvrgSK8fmvffW8ewrfMw4fsntvQv1WBGMF8k8XEKZCj97P4='
ENC_VALUE = ('AQADZA64Ih5HX2h0PBvOYhx51puUQNh1xRCQmmAjMrS6RxR6YlULlyMTuZkQb8c5z7IWl5LksQAqq4jO4hH/pA'
             '9zK2wESFHv7xg/MVdkmTNQvSHzBQ==')
EXPECT_SECRET = 'nfln/MMBxTjyEYvvQu09J4CvBpcSU7P+B9oI9sRDCGo='
EXPECT_SIV_KEY = bytes(range(64))
EXPECT_GCM_KEY = bytes(range(32, 64))


class WireSecureStoreTest(unittest.TestCase):
    def test_keyset_selects_primary_and_right_field(self):
        siv_material, siv_prefix, siv_type = wire._tink_keyset(KS_KEYS)  # pylint: disable=protected-access
        self.assertEqual(siv_material, EXPECT_SIV_KEY)  # primary, not the decoy first key
        self.assertEqual(siv_prefix, b'\x01' + struct.pack('>I', 111111))
        self.assertEqual(siv_type, wire._AES_SIV_TYPE)  # pylint: disable=protected-access
        gcm_material, _gcm_prefix, gcm_type = wire._tink_keyset(KS_VALS)  # pylint: disable=protected-access
        self.assertEqual(gcm_material, EXPECT_GCM_KEY)  # AesGcmKey keeps key_value in field 3
        self.assertEqual(gcm_type, wire._AES_GCM_TYPE)  # pylint: disable=protected-access

    def _tree(self, enc_name=ENC_NAME, enc_value=ENC_VALUE):
        root = tempfile.TemporaryDirectory()
        base = pathlib.Path(root.name)
        secrets = base / 'extra/Secrets/secrets.json'
        secrets.parent.mkdir(parents=True)
        secrets.write_text(json.dumps([{
            'app': 'com.wire', 'user_id': 0,
            'script_output': [{'payload': {
                'encrypted_prefs_keys_key': KS_KEYS, 'encrypted_prefs_values_key': KS_VALS}}]}]))
        prefs = base / 'data/data/com.wire/shared_prefs/app-preference.xml'
        prefs.parent.mkdir(parents=True)
        prefs.write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n<map>'
            '<string name="__androidx_security_crypto_encrypted_prefs_key_keyset__">x</string>'
            f'<string name="{enc_name}">{enc_value}</string></map>')
        return root, str(secrets), str(prefs)

    def test_prefs_decrypt_cross_implementation(self):
        root, secrets, prefs = self._tree()
        try:
            keyset = next(iter(wire._wire_keysets([secrets]).values()))  # pylint: disable=protected-access
            names = wire._wire_prefs(prefs, keyset)  # pylint: disable=protected-access
            self.assertIn('global_db_passphrase_alias_v2', names)
            value = wire._wire_pref_string(keyset, *names['global_db_passphrase_alias_v2'])  # pylint: disable=protected-access
            self.assertEqual(value, EXPECT_SECRET)
        finally:
            root.cleanup()

    def test_wrong_associated_data_is_rejected(self):
        root, secrets, prefs = self._tree()
        try:
            keyset = next(iter(wire._wire_keysets([secrets]).values()))  # pylint: disable=protected-access
            _encrypted_name, encrypted_value = wire._wire_prefs(prefs, keyset)['global_db_passphrase_alias_v2']  # pylint: disable=protected-access
            # the value is bound to its own encrypted name as associated data; a different name must fail
            self.assertIsNone(wire._wire_pref_string(keyset, 'AQABwrongname==', encrypted_value))  # pylint: disable=protected-access
        finally:
            root.cleanup()

    def test_db_key_v2_is_raw_legacy_is_derived(self):
        secret = base64.b64encode(bytes(range(32))).decode()
        with tempfile.NamedTemporaryFile() as handle:
            handle.write(b'\x11' * 16 + b'\x00' * 4080)
            handle.flush()
            raw = wire._wire_db_key(secret, True, handle.name)  # pylint: disable=protected-access
            derived = wire._wire_db_key(secret, False, handle.name)  # pylint: disable=protected-access
        self.assertEqual(raw, bytes(range(32)))
        self.assertEqual(len(derived), 32)
        self.assertNotEqual(raw, derived)  # a legacy secret is a passphrase, not the key

    def test_filename_domain_transform(self):
        self.assertEqual(wire._wire_filter_name('wire.com'), 'wirecom')  # pylint: disable=protected-access
        self.assertEqual(wire._wire_filter_name('12345678-90ab-4cde-8f01-234567890abc'),  # pylint: disable=protected-access
                         '12345678-90ab-4cde-8f01-234567890abc')


if __name__ == '__main__':
    unittest.main()
