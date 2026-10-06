"""Chosen prefix icon bytes remain available to media export."""
import io
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from PIL import Image  # pylint: disable=wrong-import-position
from scripts.artifacts.appicons import appIcons  # pylint: disable=wrong-import-position


def make_database(root, optional=True):
    """Create distinct valid PNG BLOBs for every selection branch."""
    path = pathlib.Path(root) / 'data/data/com.google.android.apps.nexuslauncher/databases/app_icons.db'
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE icons(componentName,profileid,lastUpdated' +
                (',version' if optional else '') + ',icon,label)')
    components = ['a.single/other.Activity', 'b.exact/b.exact.', 'b.exact/other.Activity',
                  'c.prefix/c.prefix.Alpha', 'c.prefix/c.prefix.Beta', 'c.prefix/other.Activity',
                  'd.none/first.Activity', 'd.none/other.Activity',
                  'e.null/e.null.Alpha', 'e.null/other.Activity']
    expected = {}
    for index, component in enumerate(components):
        buffer = io.BytesIO()
        Image.new('RGB', (2, 2), (index * 20, 100, 150)).save(buffer, format='PNG')
        data = None if component=='e.null/e.null.Alpha' else buffer.getvalue()
        label = 'Label' + str(index)
        values = (component, 0, 1700000000 + index) + ((1,) if optional else ()) + (data, label)
        con.execute('INSERT INTO icons VALUES(' + ','.join('?' * len(values)) + ')', values)
        expected[label] = data
    con.commit()
    assert con.execute('PRAGMA quick_check').fetchone()[0]=='ok'
    con.close()
    return path, expected


class AppIconsPrefixRetentionTest(unittest.TestCase):
    def run_projection(self, root, optional=True):
        path, expected = make_database(root, optional)
        exports = pathlib.Path(root) / 'exports'
        exports.mkdir()
        def export(source, data, name):
            self.assertEqual(source, str(path))
            if not data:
                return None
            target = exports / (name + '.png')
            target.write_bytes(data)
            with Image.open(target) as image:
                image.load()
            return str(target)
        with patch('scripts.artifacts.appicons.check_in_embedded_media', side_effect=export):
            headers, rows, source = appIcons.__wrapped__(SimpleNamespace(get_files_found=lambda: [str(path)]))
        self.assertEqual(headers, ('App name', 'Package name', ('Main icon', 'media'), ('Icons', 'media')))
        self.assertEqual(source, str(path))
        self.assertEqual([row[1] for row in rows], ['a.single','b.exact','c.prefix','d.none','e.null'])
        self.assertEqual([row[0] for row in rows], ['Label0','Label1','Label3','','Label8'])
        self.assertEqual([pathlib.Path(row[2]).stem if row[2] else None for row in rows],
                         ['Label0','Label1','Label3',None,None])
        self.assertEqual([[pathlib.Path(p).stem for p in row[3]] for row in rows],
                         [[],['Label2'],['Label4','Label5'],['Label6','Label7'],['Label9']])
        for target in exports.iterdir():
            self.assertEqual(target.read_bytes(), expected[target.stem])
        self.assertEqual(len(list(exports.iterdir())), 9)

    def test_all_selection_branches_and_null_selected_blob(self):
        with tempfile.TemporaryDirectory() as root:
            self.run_projection(root)

    def test_missing_version_column_preserves_projection(self):
        with tempfile.TemporaryDirectory() as root:
            self.run_projection(root, optional=False)
