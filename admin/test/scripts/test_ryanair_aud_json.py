"""Exercise XML and real JWT payload decoding without validating token authenticity."""
import base64
import json
import math
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import ryanair


class TestRyanairAudJSON(unittest.TestCase):
    def parse(self, claims, missing=False):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'MyRyanair_RememberMeToken.xml'
            payload = {'iat': 1704164645, 'exp': 1704168245, 'sub': 'synthetic'}
            if not missing:
                payload['aud'] = claims
            wire = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
            path.write_text('<map><string name="token">h.' + wire + '.s</string></map>')
            context = SimpleNamespace(get_files_found=lambda: [path],
                                      get_relative_path=lambda _: path.name)
            return ryanair.ryanair_sessions.__wrapped__(context)

    def test_presence_and_typed_payloads(self):
        self.assertEqual(self.parse(None, missing=True)[1][0][6], '')
        for value in [None, False, True, 0, -1, 1.25, '', '0', 'Ω\n', [], {},
                      [None, False, {'nested': 10 ** 100}], 10 ** 100, -(10 ** 100),
                      '\ud800', '\udfff', {'\ud800': '\udfff'}]:
            with self.subTest(value_type=type(value).__name__):
                headers, rows, source = self.parse(value)
                self.assertEqual(len(headers), 9)
                self.assertEqual(len(rows[0]), 9)
                encoded = rows[0][6]
                self.assertIsInstance(encoded, str)
                self.assertTrue(encoded.isascii())
                self.assertEqual(json.loads(encoded), value)
                self.assertEqual(rows[0][3], 'synthetic')
                self.assertEqual(rows[0][7], '')
                self.assertTrue(source.endswith('MyRyanair_RememberMeToken.xml'))

    def test_nonfinite_decoder_extensions(self):
        for value in [float('nan'), float('inf'), float('-inf')]:
            decoded = json.loads(self.parse(value)[1][0][6])
            if math.isnan(value):
                self.assertTrue(math.isnan(decoded))
            else:
                self.assertEqual(decoded, value)

    def test_repeated_non_token_rows_keep_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'PreferencesBasketSessionKey.xml'
            path.write_text('<map><string name="x">opaque</string>'
                            '<string name="x">opaque</string></map>')
            context = SimpleNamespace(get_files_found=lambda: [path],
                                      get_relative_path=lambda _: path.name)
            _, rows, _ = ryanair.ryanair_sessions.__wrapped__(context)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0], rows[1])
            self.assertEqual(rows[0][6:8], ('', 'value present, not a JSON Web Token'))


if __name__ == '__main__':
    unittest.main()
