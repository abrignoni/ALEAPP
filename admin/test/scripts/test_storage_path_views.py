import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.artifacts.storagePathViews import canonical_path, unique_files


class FakeContext:
    """Stands in for the artifact Context: files_found are extracted paths and
    get_relative_path strips the run's own extraction folder."""

    def __init__(self, files, data_folder='/out/ALEAPP_Output/data'):
        self._files = list(files)
        self._data_folder = data_folder

    def get_files_found(self):
        return list(self._files)

    def get_relative_path(self, full_path):
        if self._data_folder in full_path:
            return full_path.replace(self._data_folder + '/', '').lstrip('/')
        return full_path


def extracted(*relative, data_folder='/out/ALEAPP_Output/data'):
    return [f'{data_folder}/{r}' for r in relative]


class TestCanonicalPath(unittest.TestCase):
    def test_credential_encrypted_views_share_a_key(self):
        keys = {canonical_path(p)[0] for p in (
            'Dump/data/data/com.foo/databases/x.db',
            'Dump/data/user/0/com.foo/databases/x.db',
            'Dump/data_mirror/data_ce/null/0/com.foo/databases/x.db',
        )}
        self.assertEqual(len(keys), 1)

    def test_device_encrypted_views_share_a_key(self):
        keys = {canonical_path(p)[0] for p in (
            'Dump/data/user_de/0/com.foo/databases/x.db',
            'Dump/data_mirror/data_de/null/0/com.foo/databases/x.db',
        )}
        self.assertEqual(len(keys), 1)

    def test_credential_and_device_encrypted_stay_apart(self):
        """They are different directories holding different files. pixel3_a12 carries
        com.android.providers.telephony/databases/mmssms.db in both and they differ."""
        ce, _ = canonical_path('Dump/data/data/com.foo/databases/x.db')
        de, _ = canonical_path('Dump/data/user_de/0/com.foo/databases/x.db')
        self.assertNotEqual(ce, de)

    def test_android_users_stay_apart(self):
        a, _ = canonical_path('data/user/0/com.foo/databases/x.db')
        b, _ = canonical_path('data/user/10/com.foo/databases/x.db')
        self.assertNotEqual(a, b)

    def test_data_data_outranks_the_other_spellings(self):
        ranks = {p: canonical_path(p)[1] for p in (
            'Dump/data/data/com.foo/x',
            'Dump/data/user/0/com.foo/x',
            'Dump/data_mirror/data_ce/null/0/com.foo/x',
        )}
        self.assertEqual(min(ranks, key=ranks.get), 'Dump/data/data/com.foo/x')

    def test_paths_outside_an_app_data_directory_are_untouched(self):
        for path in ('Dump/system/build.prop', 'Dump/data/media/0/DCIM/a.jpg'):
            self.assertEqual(canonical_path(path), (path, 0))


class TestUniqueFiles(unittest.TestCase):
    def test_three_views_collapse_to_the_data_data_copy(self):
        files = extracted(
            'Dump/data/user/0/com.foo/databases/x.db',
            'Dump/data_mirror/data_ce/null/0/com.foo/databases/x.db',
            'Dump/data/data/com.foo/databases/x.db',
        )
        kept = unique_files(FakeContext(files))
        self.assertEqual(kept, [f for f in files if '/data/data/' in f])

    def test_an_extraction_with_one_view_is_unchanged(self):
        files = extracted(
            'Dump/data/data/com.foo/databases/x.db',
            'Dump/data/data/com.bar/databases/y.db',
        )
        self.assertEqual(unique_files(FakeContext(files)), files)

    def test_a_file_present_only_under_a_mirror_is_kept(self):
        files = extracted('Dump/data_mirror/data_ce/null/0/com.foo/databases/x.db')
        self.assertEqual(unique_files(FakeContext(files)), files)

    def test_order_follows_first_appearance(self):
        files = extracted(
            'Dump/data/user/0/com.b/x.db',
            'Dump/data/user/0/com.a/x.db',
            'Dump/data/data/com.b/x.db',
            'Dump/data/data/com.a/x.db',
        )
        kept = unique_files(FakeContext(files))
        self.assertEqual([Path(f).parent.name for f in kept], ['com.b', 'com.a'])

    def test_the_extraction_folder_is_not_mistaken_for_evidence(self):
        """The run's own folder is named 'data', so on an extraction whose members
        start with 'data/' the on-disk path reads .../data/data/data/com.foo. Only the
        evidence relative path distinguishes the harness boundary from the evidence."""
        files = extracted('data/data/com.foo/x.db', 'data/user/0/com.foo/x.db')
        kept = unique_files(FakeContext(files))
        self.assertEqual(kept, ['/out/ALEAPP_Output/data/data/data/com.foo/x.db'])

    def test_sidecars_track_their_database(self):
        files = extracted(
            'Dump/data/data/com.foo/databases/x.db',
            'Dump/data/data/com.foo/databases/x.db-wal',
            'Dump/data/user/0/com.foo/databases/x.db',
            'Dump/data/user/0/com.foo/databases/x.db-wal',
        )
        kept = unique_files(FakeContext(files))
        self.assertTrue(all('/data/data/' in f for f in kept))
        self.assertEqual(len(kept), 2)


if __name__ == '__main__':
    unittest.main()
