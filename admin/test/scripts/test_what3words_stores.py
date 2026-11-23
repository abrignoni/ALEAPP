"""Every what3words store is read, once per storage view, and each row names its Android user."""
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import what3words

STORE = 'com.what3words.android/files/default.realm'


def run(artifact, table, relative_paths):
    """The artifact's headers, rows and source, with the Realm reader answering one row per store."""
    with tempfile.TemporaryDirectory() as folder:
        root = pathlib.Path(folder)
        files = []
        for relative in relative_paths:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'realm')
            files.append(str(path))
        context = SimpleNamespace(get_files_found=lambda: files,
                                  get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))
        with patch.object(what3words, 'parse_realm_file', return_value={'active': {table: {}}}), \
                patch.object(what3words, 'realm_rows', side_effect=lambda path, name: [{'label': path}] if name == table else []):
            headers, rows, source = getattr(what3words, artifact).__wrapped__(context)
        relative_source = [str(pathlib.Path(p).relative_to(root)) for p in source.split('\n')] if source else []
    return headers, rows, relative_source


class Stores(unittest.TestCase):
    def test_saved_places_read_every_user(self):
        headers, rows, source = run('what3words_saved_places', 'class_LocationRealm',
                                    [f'data/user/0/{STORE}', f'data/user/10/{STORE}'])
        self.assertEqual(headers[-1], 'Android User')
        self.assertEqual(sorted(r[-1] for r in rows), ['0', '10'])
        self.assertEqual(len(source), 2)

    def test_lists_read_every_user(self):
        headers, rows, source = run('what3words_lists', 'class_LocationsListsRealm',
                                    [f'data/user/0/{STORE}', f'data/user/10/{STORE}'])
        self.assertEqual(headers[-1], 'Android User')
        self.assertEqual(sorted(r[-1] for r in rows), ['0', '10'])
        self.assertEqual(len(source), 2)

    def test_storage_views_of_one_store_are_read_once(self):
        _headers, rows, source = run('what3words_saved_places', 'class_LocationRealm',
                                     [f'data/data/{STORE}', f'data/user/0/{STORE}'])
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(source), 1)

    def test_no_store_gives_no_rows(self):
        _headers, rows, source = run('what3words_saved_places', 'class_LocationRealm', [])
        self.assertEqual((rows, source), ([], []))


if __name__ == '__main__':
    unittest.main()
