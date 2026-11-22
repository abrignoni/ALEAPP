"""The provider of an external.db comes from its own package folder, never from the folders above it."""
# pylint: disable=protected-access
import pathlib
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import emulatedSmeta

MODULE = 'data/data/com.google.android.providers.media.module/databases/external.db'
LEGACY = 'data/data/com.android.providers.media/databases/external.db'


def route(*paths):
    with patch.object(emulatedSmeta, 'unique_files', return_value=list(paths)):
        return emulatedSmeta._external_dbs(object(), True), emulatedSmeta._external_dbs(object(), False)


class ProviderRouting(unittest.TestCase):
    def test_each_provider_goes_to_its_own_artifacts(self):
        module, legacy = '/cases/report/data/' + MODULE, '/cases/report/data/' + LEGACY
        self.assertEqual(route(module, legacy), ([module], [legacy]))

    def test_output_folder_name_does_not_change_the_route(self):
        root = '/cases/media.module review/report/data/'
        module, legacy = root + MODULE, root + LEGACY
        self.assertEqual(route(module, legacy), ([module], [legacy]))

    def test_windows_separators(self):
        root = 'C:\\cases\\media.module review\\data\\'
        module, legacy = root + MODULE.replace('/', '\\'), root + LEGACY.replace('/', '\\')
        self.assertEqual(route(module, legacy), ([module], [legacy]))

    def test_sidecars_are_not_routed(self):
        self.assertEqual(route('/r/data/' + MODULE + '-wal', '/r/data/' + LEGACY + '-shm'), ([], []))


if __name__ == '__main__':
    unittest.main()
