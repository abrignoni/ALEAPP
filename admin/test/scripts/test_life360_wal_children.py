"""Snapshot-reachable child records and schema-proven signed rowid aliases."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from admin.test.scripts.test_life360_wal_schema import create_pair
from scripts.artifacts import L360noshowalerts as module


class TestLife360WalChildren(unittest.TestCase):
    def test_checkpointed_interior_child_frames(self):
        with tempfile.TemporaryDirectory() as root:
            main = create_pair(root, count=150, checkpoint_tree=True)
            connection = sqlite3.connect(main.as_uri()+'?mode=ro', uri=True)
            rootpage = connection.execute("SELECT rootpage FROM sqlite_master "
                                          "WHERE name='no_show_alerts'").fetchone()[0]
            connection.close()
            self.assertEqual(main.read_bytes()[(rootpage-1)*512], 5)
            with patch.object(module, 'logfunc'):
                rows = module.recover_wal_observations(main, Path(str(main)+'-wal'))
            self.assertGreater(len(rows), 2)  # Neighboring records in each observed leaf survive.
            self.assertTrue(all(r['_wal_page'] != rootpage for r in rows))
            changed = {r['id'] for r in rows if r['last_updated'] == 1700000002000}
            self.assertEqual(changed, {'id0', 'id149'})
            self.assertTrue(all(r['id'].startswith('id') for r in rows))
            self.assertEqual(len({r['_wal_frame'] for r in rows}), 2)

    def test_signed_rowid_with_reordered_schema(self):
        with tempfile.TemporaryDirectory() as root:
            for index, identifier in enumerate([-1, 0, 42, -(1 << 63), (1 << 63)-1]):
                main = create_pair(root, str(index), integer_pk=True, reordered=True,
                                   rowid_value=identifier)
                with patch.object(module, 'logfunc'):
                    rows = module.recover_wal_observations(main, Path(str(main)+'-wal'))
                self.assertEqual([r['id'] for r in rows], [identifier, identifier])
                self.assertTrue(all(r['trigger_condition'] == 'trigger' for r in rows))

    def test_ambiguous_primary_key_layouts_are_not_guessed(self):
        with tempfile.TemporaryDirectory() as root:
            layouts = [('id INTEGER PRIMARY KEY DESC', None),
                       ('id INT PRIMARY KEY', None),
                       ('id INTEGER', 'PRIMARY KEY(id,type)')]
            for index, (declaration, tail) in enumerate(layouts):
                main = create_pair(root, str(index), integer_pk=True,
                                   pk_declaration=declaration, pk_tail=tail)
                with patch.object(module, 'logfunc') as log:
                    rows = module.recover_wal_observations(main, Path(str(main)+'-wal'))
                self.assertEqual(rows, [])
                self.assertTrue(any('PRIMARY KEY' in call.args[0]
                                    for call in log.call_args_list))

    def test_invalid_ownership_graph_and_unrelated_leaf(self):
        with tempfile.TemporaryDirectory() as root:
            main = create_pair(root, count=150, checkpoint_tree=True)
            image = bytearray(main.read_bytes())
            connection = sqlite3.connect(main.as_uri()+'?mode=ro', uri=True)
            rootpage = connection.execute("SELECT rootpage FROM sqlite_master "
                                          "WHERE name='no_show_alerts'").fetchone()[0]
            unrelated = connection.execute("SELECT rootpage FROM sqlite_master "
                                           "WHERE name='unrelated0'").fetchone()[0]
            connection.close()
            leaves, failure = module.reachable_table_leaves(image, rootpage, 512, 512)
            self.assertIsNone(failure)
            self.assertNotIn(unrelated, leaves)
            offset = (rootpage-1)*512
            for pointer in [rootpage, len(image)//512+1, 0]:
                broken = bytearray(image)
                broken[offset+8:offset+12] = pointer.to_bytes(4, 'big')
                leaves, failure = module.reachable_table_leaves(broken, rootpage, 512, 512)
                self.assertEqual(leaves, set())
                self.assertIn('unproven', failure)
            for header_change in ['oversized array', 'invalid cell pointer', 'duplicate child']:
                broken = bytearray(image)
                if header_change == 'oversized array':
                    broken[offset+3:offset+5] = b'\xff\xff'
                elif header_change == 'invalid cell pointer':
                    broken[offset+12:offset+14] = (511).to_bytes(2, 'big')
                else:
                    first_cell = int.from_bytes(broken[offset+12:offset+14], 'big')
                    broken[offset+8:offset+12] = broken[offset+first_cell:offset+first_cell+4]
                self.assertTrue(module.reachable_table_leaves(
                    broken, rootpage, 512, 512)[1])
            broken = bytearray(image)
            broken[offset] = 2
            self.assertTrue(module.reachable_table_leaves(broken, rootpage, 512, 512)[1])


if __name__ == '__main__':
    unittest.main()
