"""Line evidence retains file/user identity, repeats, endings and invalid bytes."""
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from scripts.artifacts import GarminLog as garmin
from admin.test.scripts.test_history_doclist_all_sources import Context


FIRST = (b'ordinary line\n'
         b'access_token: "first:https://example.test/a==",\r\n'
         b'access_token: "first:https://example.test/a==",\r\n'
         b'Authorization: access_token=a==, refresh_token=b=c\n'
         b'Authorization: access_token=later==, id_token=next\n'
         b'refresh_token without colon or equals\n'
         b'access_token: invalid \xff\\xff <log>\n'
         b'ACCESS_TOKEN: ignored\n')
SECOND = b'expires_in: 3600\nAuthorization: token_type=Bearer, id_token=other=='


def create_log_fixture(root, edge=False):
    root = Path(root)
    sources = [(root/'A/data/data/com.garmin.android.apps.connectmobile/files/logs/app.log', FIRST),
               (root/'A/data/data/com.garmin.android.apps.connectmobile/files/logs/app.log.1', SECOND),
               (root/'A/data/user/10/com.garmin.android.apps.connectmobile/files/logs/app.log', SECOND)]
    files = []
    for path, content in sources:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        files.append(path)
    original = sources[0][0]
    for view in ['A/data/user/0', 'A/data_mirror/data_ce/null/0']:
        alias = root/view/'com.garmin.android.apps.connectmobile/files/logs/app.log'
        alias.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, alias)
        files.append(alias)
    if edge:
        files.append(root/'missing/app.log')
    return files


class TestGarminLogEvidence(unittest.TestCase):
    def test_sources_repeats_full_values_and_encoding_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_log_fixture(directory)
            headers, rows, sources = garmin.get_log.__wrapped__(Context(directory, list(reversed(files))))
            self.assertEqual(len(rows), 10)
            self.assertEqual(rows, garmin.get_log.__wrapped__(Context(directory, files))[1])
            self.assertEqual(len(sources.splitlines()), 3)
            self.assertEqual(headers[0], 'Line Number')
            self.assertEqual([r[0] for r in rows[:6]], [2, 3, 4, 5, 6, 7])
            self.assertEqual(rows[0][2], rows[1][2])
            self.assertEqual(rows[0][2], 'access_token: "first:https://example.test/a==",\r\n')
            self.assertEqual(rows[2][1], 'access_token, refresh_token, Authorization')
            self.assertEqual(rows[3][1], 'access_token, id_token, Authorization')
            self.assertIn('Invalid UTF-8', rows[5][4])
            self.assertEqual(rows[5][2], 'access_token: invalid \\xff\\xff <log>\n')
            self.assertNotEqual(bytes.fromhex(rows[5][3]), rows[5][2].encode())
            for row in rows:
                original = Path(directory, row[-1]).read_bytes().splitlines(keepends=True)
                self.assertEqual(bytes.fromhex(row[3]), original[row[0]-1])
            self.assertFalse(rows[-1][2].endswith('\n'))
            staged = Path(directory)/'mirror-staged/user/0'
            shutil.copytree(Path(directory)/'A', staged/'A')
            staged_files = [staged/p.relative_to(directory) for p in files]
            self.assertEqual(garmin.get_log.__wrapped__(Context(staged, staged_files))[1], rows)


    def test_empty_mirror_only_and_read_error_continue(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_log_fixture(directory, edge=True)
            self.assertEqual(garmin.get_log.__wrapped__(Context(directory, []))[1], [])
            mirror = [p for p in files if 'data_mirror/' in str(p)]
            self.assertEqual(len(garmin.get_log.__wrapped__(Context(directory, mirror))[1]), 6)
            with patch.object(garmin, 'logfunc') as logs:
                self.assertEqual(len(garmin.get_log.__wrapped__(Context(directory, files))[1]), 10)
            self.assertTrue(any('missing/app.log' in str(c) for c in logs.call_args_list))


if __name__ == '__main__':
    unittest.main()
