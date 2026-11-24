"""Every what3words store is read, once per storage view, and each row names its Android user and Realm version."""
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
                patch.object(what3words, 'realm_rows', side_effect=lambda path, name, section='active': [{'label': path}] if name == table else []):
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



def run_versions(artifact, table, active, inactive):
    """Rows for one store whose active and inactive versions hold the given rows."""
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / f'data/data/{STORE}'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'realm')
        context = SimpleNamespace(get_files_found=lambda: [str(path)],
                                  get_relative_path=lambda p: str(pathlib.Path(p).relative_to(folder)))
        sections = {'active': active, 'inactive': inactive}
        with patch.object(what3words, 'parse_realm_file', return_value={'active': {table: {}}}), \
                patch.object(what3words, 'realm_rows',
                             side_effect=lambda _path, name, section='active': sections[section] if name == table else []):
            headers, rows, _source = getattr(what3words, artifact).__wrapped__(context)
    return headers, rows


class Versions(unittest.TestCase):
    SAME = {'id': 'a', 'label': 'same'}
    OLD = {'id': 'b', 'label': 'same'}

    def test_an_inactive_row_not_in_the_active_version_is_reported(self):
        headers, rows = run_versions('what3words_saved_places', 'class_LocationRealm',
                                     [self.SAME], [self.SAME, self.OLD])
        version = headers.index('Realm Version')
        ident = headers.index('id (as stored)')
        self.assertEqual(sorted((r[ident], r[version]) for r in rows), [('a', 'Active'), ('b', 'Inactive')])

    def test_an_inactive_row_identical_to_an_active_row_is_not_repeated(self):
        _headers, rows = run_versions('what3words_saved_places', 'class_LocationRealm', [self.SAME], [self.SAME])
        self.assertEqual(len(rows), 1)

    def test_lists_report_inactive_rows_too(self):
        headers, rows = run_versions('what3words_lists', 'class_LocationsListsRealm', [], [self.OLD])
        self.assertEqual([r[headers.index('Realm Version')] for r in rows], ['Inactive'])

    def test_a_changed_row_appears_in_both_versions(self):
        changed = dict(self.SAME, label='earlier')
        headers, rows = run_versions('what3words_saved_places', 'class_LocationRealm', [self.SAME], [changed])
        self.assertEqual(sorted(r[headers.index('Realm Version')] for r in rows), ['Active', 'Inactive'])


class ListIds(unittest.TestCase):
    def cell(self, value):
        headers, rows = run_versions('what3words_saved_places', 'class_LocationRealm',
                                     [{'id': 'a', 'listIds': value}], [])
        return rows[0][headers.index('listIds (as stored)')]

    def test_one_list_id_is_shown(self):
        self.assertEqual(self.cell([123]), '123')

    def test_several_list_ids_are_joined_in_stored_order(self):
        self.assertEqual(self.cell([5, 3]), '5, 3')

    def test_no_list_id_is_blank(self):
        self.assertEqual(self.cell([]), '')
        self.assertEqual(self.cell(None), '')


if __name__ == '__main__':
    unittest.main()
