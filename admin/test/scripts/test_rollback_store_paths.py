"""Which rollback.json paths rollbackStore reads (constructed paths only)."""
import unittest

from scripts.artifacts import rollbackStore


class TestRollbackStorePaths(unittest.TestCase):
    def test_store_under_data_and_at_a_partition_root(self):
        self.assertEqual(rollbackStore._store('x/Dump/data/rollback/12/rollback.json'), 'rollback')
        self.assertEqual(rollbackStore._store('x/data/rollback-history/12-0a1b/rollback.json'),
                         'rollback-history')
        self.assertEqual(rollbackStore._store('report/data/lba0/rollback/12/rollback.json'), 'rollback')
        self.assertEqual(rollbackStore._store('lba0/rollback-history/12-0a1b/rollback.json'),
                         'rollback-history')

    def test_app_folders_and_other_folder_names_are_not_read(self):
        for path in ('x/data/data/com.example.app/files/rollback/12/rollback.json',
                     'lba0/data/com.example.app/rollback/12/rollback.json',
                     'lba0/user/0/com.example.app/rollback/12/rollback.json',
                     'lba0/media/0/Android/data/com.example.app/rollback/12/rollback.json',
                     'x/data/rollback/notanumber/rollback.json',
                     'x/data/rollback/12/other.json'):
            self.assertIsNone(rollbackStore._store(path), path)


if __name__ == '__main__':
    unittest.main()
