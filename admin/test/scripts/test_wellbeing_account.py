"""wellbeingaccount decodes AccountData.pb with the vendored blackboxprotobuf.

It reports one row per distinct file per Android user.

The payloads are synthetic, encoded by hand here, so no value comes from an extraction. The
cases are the owner's file under /data/data and /data/user/0 with the same bytes (one row), a
second user under /data/user/10 (its own row), text and non-text byte values, and a file that
is not a protobuf (skipped and logged, not a crash).
"""
import json
import pathlib
import shutil
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from scripts.artifacts import wellbeingaccount

PKG = 'com.google.android.apps.wellbeing/files/AccountData.pb'


def _field(number, data):
    """A length-delimited protobuf field (wire type 2); every length here is under 128."""
    assert len(data) < 128
    return bytes([number << 3 | 2, len(data)]) + data


def payload(name, blob=b'\x00\xff'):
    """Field 1 = varint 3; field 2 = a message holding field 1 = name and field 2 = blob."""
    return b'\x08\x03' + _field(2, _field(1, name.encode('utf-8')) + _field(2, blob))


class WellbeingAccountTests(unittest.TestCase):

    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _file(self, prefix, content):
        path = self.root / prefix / PKG
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return str(path)

    def _run(self, paths):
        context = SimpleNamespace(get_files_found=lambda: paths,
                                  get_relative_path=lambda path: path)
        return wellbeingaccount.get_wellbeingaccount.__wrapped__(context)

    def test_one_row_per_user_and_the_owner_copies_collapse(self):
        owner = payload('owner')
        paths = [self._file('data/data', owner), self._file('data/user/0', owner),
                 self._file('data/user/10', payload('second'))]

        headers, rows, source = self._run(paths)

        self.assertEqual(headers, ('Android User', 'Protobuf Parsed Data', 'Protobuf Data'))
        self.assertEqual([row[0] for row in rows], ['0', '10'])
        self.assertEqual(len(source.split('\n')), 2)
        decoded = [json.loads(row[2]) for row in rows]
        self.assertEqual([d['2']['1'] for d in decoded], ['owner', 'second'])
        self.assertEqual(decoded[0]['2']['2'], '00ff')   # not UTF-8, so hex
        self.assertEqual(decoded[0]['1'], 3)

    def test_the_html_cell_stays_on_one_line(self):
        _, rows, _ = self._run([self._file('data/data', payload('a<b'))])
        cell = rows[0][1]
        self.assertNotIn('\n', cell)
        self.assertIn('&lt;', cell)
        self.assertTrue(cell.startswith('<pre id="json">') and cell.endswith('</pre>'))

    def test_two_different_owner_copies_both_report(self):
        paths = [self._file('data/data', payload('one')), self._file('data/user/0', payload('two'))]
        _, rows, _ = self._run(paths)
        self.assertEqual([row[0] for row in rows], ['0', '0'])

    def test_a_file_that_is_not_a_protobuf_is_logged_and_skipped(self):
        bad = self._file('data/user/10', b'\xff\xff\xff\xff')
        good = self._file('data/data', payload('owner'))
        with mock.patch.object(wellbeingaccount, 'logfunc') as log:
            _, rows, source = self._run([bad, good])
        self.assertEqual([row[0] for row in rows], ['0'])
        self.assertEqual(source, good)
        self.assertTrue(any('could not be decoded' in str(call) for call in log.call_args_list))

    def test_a_path_outside_a_user_directory_has_no_user(self):
        self.assertEqual(wellbeingaccount._android_user(f'/x/elsewhere/{PKG}'), '')  # pylint: disable=protected-access
        self.assertEqual(wellbeingaccount._android_user(f'C:\\x\\data\\user\\11\\{PKG}'.replace('/', '\\')), '11')  # pylint: disable=protected-access


if __name__ == '__main__':
    unittest.main()
