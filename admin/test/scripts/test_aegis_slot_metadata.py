"""Actual JSON inputs distinguish unavailable slot metadata from a recorded zero."""
import json
import pathlib
import tempfile
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts.aegis import aegis_vault, aegis_entries  # pylint: disable=wrong-import-position


class AegisSlotMetadataTest(unittest.TestCase):
    def project(self, vaults):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            paths = []
            for index, vault in enumerate(vaults):
                path = root / str(index) / 'com.beemdevelopment.aegis/files/aegis.json'
                path.parent.mkdir(parents=True)
                path.write_text(json.dumps(vault), encoding='utf-8')
                paths.append(str(path))
            context = SimpleNamespace(get_files_found=lambda: paths,
                                      get_relative_path=lambda path: str(pathlib.Path(path).relative_to(root)))
            with patch('scripts.artifacts.aegis.logfunc'):
                summary = aegis_vault.__wrapped__(context)
                entries = aegis_entries.__wrapped__(context)
            return summary, entries

    def test_encrypted_json_unknown_slots_and_explicit_list_counts(self):
        headers = [{}, {'slots': None}, {'slots': {}}, {'slots': 'metadata'},
                   {'slots': []}, {'slots': [{}]}, {'slots': [{}, {}]}]
        vaults = [{'version': 1, 'db': 'opaque', 'header': header} for header in headers]
        vaults.insert(0, {'version': 1, 'db': 'opaque'})
        (columns, rows, sources), (_, entries, entry_sources) = self.project(vaults)
        self.assertEqual(columns[-1], 'Source File')
        self.assertEqual([row[2] for row in rows], ['Encrypted (slot count unknown)'] * 5 +
                         ['Encrypted (0 slots)', 'Encrypted (1 slots)', 'Encrypted (2 slots)'])
        self.assertTrue(all(row[:2] == (1, '') and row[3] == 'Unknown (encrypted)' for row in rows))
        self.assertEqual([row[-1].split('/')[0] for row in rows], [str(index) for index in range(8)])
        self.assertEqual(len(sources.splitlines()), 8)
        self.assertEqual(entries, [])
        self.assertEqual(entry_sources, '')

    def test_non_object_headers_are_unavailable_without_changing_db_detection(self):
        vaults = [{'db': 'opaque', 'header': header} for header in [None, 'metadata', [], ['slot'], 1, True]]
        (_, rows, _), (_, entries, _) = self.project(vaults)
        self.assertTrue(all(row[2] == 'Encrypted (slot count unknown)' for row in rows))
        self.assertEqual(entries, [])

    def test_plaintext_entries_and_existing_truthy_slot_detection_remain(self):
        entry = {'uuid': 'entry', 'type': 'totp', 'issuer': 'Issuer', 'name': 'Name',
                 'info': {'algo': 'SHA1', 'digits': 6, 'period': 30, 'secret': 'not-reported'}}
        db = {'version': 2, 'entries': [entry]}
        vaults = [{'version': 1, 'db': db, 'header': header}
                  for header in [{}, {'slots': None}, {'slots': []}, {'slots': {}},
                                 {'slots': 'metadata'}, {'slots': {'key': 1}}, 'metadata']]
        (_, rows, _), (columns, entries, sources) = self.project(vaults)
        self.assertEqual([row[2] for row in rows], ['None (plaintext)'] * 4 +
                         ['Encrypted (slot count unknown)'] * 2 + ['None (plaintext)'])
        self.assertTrue(all(row[:2] == (1, 2) and row[3] == 1 for row in rows))
        self.assertEqual(len(entries), 7)
        self.assertEqual(len(sources.splitlines()), 7)
        self.assertNotIn('Secret', columns)
        self.assertTrue(all(row[:6] == ('totp', 'Issuer', 'Name', 'SHA1', 6, 30) for row in entries))
        self.assertTrue(all('not-reported' not in row for row in entries))


if __name__ == '__main__':
    unittest.main()
