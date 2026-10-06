"""Independent SQLite states and stored profiles keep their own icon bytes."""
import builtins
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from admin.test.scripts.test_appicons_prefix_retention import make_database  # pylint: disable=wrong-import-position
from scripts.artifacts.appicons import appIcons, _app_icon_sources  # pylint: disable=wrong-import-position

TAIL = 'com.google.android.apps.nexuslauncher/databases/app_icons.db'


def context(root, paths):
    return SimpleNamespace(get_files_found=lambda: list(map(str, paths)),
                           get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))


def copy_to(path, root, prefix):
    target = pathlib.Path(root) / prefix / TAIL
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    return target


def make_profiles(root, missing=False):
    path, _ = make_database(root)
    con = sqlite3.connect(path)
    blobs = [r[0] for r in con.execute('SELECT icon FROM icons WHERE icon IS NOT NULL')]
    con.execute('DROP TABLE icons')
    con.execute('CREATE TABLE icons(componentName' + ('' if missing else ',profileid') +
                ',lastUpdated,version,icon,label)')
    rows = []
    for index, profile in enumerate([0, '0', 0.0, None, 10]):
        rows.append(('same.pkg/same.pkg.Alpha', profile, 1700000000, 1, blobs[index], 'P' + str(index)))
        rows.append(('same.pkg/z.Other', profile, 1700000000, 1, blobs[index + 1], 'Other' + str(index)))
    # Legacy same-profile/component replacement stays confined to integer10.
    rows.append(('same.pkg/same.pkg.Alpha', 10, 1700000000, 1, blobs[7], 'Replacement'))
    if missing:
        rows = [row[:1] + row[2:] for row in rows[:2]]
    con.executemany('INSERT INTO icons VALUES(' + ','.join('?' * len(rows[0])) + ')', rows)
    con.commit()
    con.close()
    return path


def make_wal_pair(root):
    path, _ = make_database(pathlib.Path(root) / 'live')
    con = sqlite3.connect(path)
    con.execute('PRAGMA journal_mode=WAL')
    con.execute('PRAGMA wal_autocheckpoint=0')
    con.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    con.execute("UPDATE icons SET label='WAL-one' WHERE componentName='a.single/other.Activity'")
    con.commit()
    first = copy_to(path, root, 'data/data')
    shutil.copy2(str(path) + '-wal', str(first) + '-wal')
    con.execute("UPDATE icons SET label='WAL-two' WHERE componentName='a.single/other.Activity'")
    con.commit()
    second = copy_to(path, root, 'data/user/0')
    shutil.copy2(str(path) + '-wal', str(second) + '-wal')
    con.close()
    assert first.read_bytes()==second.read_bytes()
    return first, second


class AppIconsSourceProfilesTest(unittest.TestCase):
    def test_typed_profiles_interleaved_components_and_confined_duplicate(self):
        with tempfile.TemporaryDirectory() as root:
            path = make_profiles(root)
            captured = []
            def export(source, data, name):
                captured.append((source, data, name))
                return name
            with patch('scripts.artifacts.appicons.check_in_embedded_media', side_effect=export):
                headers, rows, source = appIcons.__wrapped__(context(root, [path]))
            self.assertEqual(headers[-1], 'Profile ID (as stored)')
            self.assertEqual([(type(r[4]).__name__, r[4]) for r in rows],
                             [('int',0),('str','0'),('float',0.0),('NoneType',None),('int',10)])
            self.assertEqual([r[0] for r in rows], ['P0','P1','P2','P3','Replacement'])
            self.assertEqual([r[3] for r in rows], [['Other' + str(i)] for i in range(5)])
            self.assertEqual(source, str(path))
            con = sqlite3.connect(path)
            for _, data, label in captured:
                self.assertEqual(data, con.execute('SELECT icon FROM icons WHERE label=?',(label,)).fetchone()[0])
            con.close()

    def test_missing_profile_is_unknown(self):
        with tempfile.TemporaryDirectory() as root:
            path = make_profiles(root, missing=True)
            with patch('scripts.artifacts.appicons.check_in_embedded_media', return_value='media'):
                _, rows, _ = appIcons.__wrapped__(context(root, [path]))
            self.assertEqual(len(rows), 1)
            self.assertIsNone(rows[0][4])

    def test_aliases_namespace_and_sidecar_complete_fingerprints(self):
        with tempfile.TemporaryDirectory() as root:
            main, _ = make_database(root)
            alias = copy_to(main, root, 'data/user/0')
            mirror = copy_to(main, root, 'data_mirror/data_ce/null/0')
            user10 = copy_to(main, root, 'data/user/10')
            device = copy_to(main, root, 'data/user_de/0')
            unknown = copy_to(main, root, 'unknown/data/data')
            for path in [main, alias, mirror]:
                pathlib.Path(str(path) + '-journal').write_bytes(b'')
            pathlib.Path(str(alias) + '-shm').write_bytes(b'index differs')
            paths = [main, alias, mirror, user10, device, unknown]
            self.assertEqual(_app_icon_sources(context(root, paths)), list(map(str,[main,user10,device,unknown])))
            pathlib.Path(str(alias) + '-journal').unlink()
            pathlib.Path(str(mirror) + '-journal').write_bytes(b'fingerprint-only journal fixture')
            self.assertEqual(_app_icon_sources(context(root, paths)), list(map(str,paths)))

    def test_actual_wal_difference_preserves_both_alias_states_and_source_rows(self):
        with tempfile.TemporaryDirectory() as root:
            paths = tuple(reversed(make_wal_pair(root)))
            self.assertEqual(_app_icon_sources(context(root, paths)), list(map(str,paths)))
            with patch('scripts.artifacts.appicons.check_in_embedded_media', side_effect=lambda p,d,n:n):
                headers, rows, source = appIcons.__wrapped__(context(root, paths))
            self.assertEqual(headers[-1], 'Source File')
            self.assertEqual(len(rows), 10)
            self.assertEqual([rows[0][0], rows[5][0]], ['WAL-two','WAL-one'])
            self.assertEqual([r[-1] for r in rows[:5]], [str(paths[0].relative_to(root))]*5)
            self.assertEqual([r[-1] for r in rows[5:]], [str(paths[1].relative_to(root))]*5)
            self.assertEqual(source.splitlines(), list(map(str,paths)))

    def test_exact_main_filter_errors_and_only_successful_row_origins(self):
        with tempfile.TemporaryDirectory() as root:
            main, _ = make_database(root)
            empty = copy_to(main, root, 'data/user/10')
            con = sqlite3.connect(empty); con.execute('DELETE FROM icons'); con.commit(); con.close()
            unsupported = copy_to(main, root, 'data/user/11')
            con = sqlite3.connect(unsupported); con.execute('DROP TABLE icons'); con.commit(); con.close()
            invalid = pathlib.Path(root) / 'bad' / TAIL
            invalid.parent.mkdir(parents=True); invalid.write_bytes(b'not SQLite')
            backup = pathlib.Path(str(main)+'.bak'); shutil.copy2(main,backup)
            paths = [main, empty, unsupported, invalid, backup, pathlib.Path(str(main)+'-wal'), main.parent]
            with patch('scripts.artifacts.appicons.check_in_embedded_media', return_value='media'), \
                 patch('scripts.artifacts.appicons.logfunc') as log:
                headers, rows, source = appIcons.__wrapped__(context(root,paths))
            self.assertEqual(len(rows),5)
            self.assertNotIn('Source File',headers)
            self.assertEqual(source,str(main))
            self.assertTrue(any('unsupported SQLite header' in c.args[0] for c in log.call_args_list))
            self.assertTrue(any('unsupported icons schema' in c.args[0] for c in log.call_args_list))

    def test_unreadable_sidecar_is_not_treated_as_absent(self):
        with tempfile.TemporaryDirectory() as root:
            main, _ = make_database(root)
            alias = copy_to(main,root,'data/user/0')
            original_open = builtins.open
            def guarded(path, *args, **kwargs):
                if str(path)==str(main)+'-wal':
                    raise PermissionError('fixture blocked sidecar')
                return original_open(path,*args,**kwargs)
            with patch('builtins.open',side_effect=guarded), patch('scripts.artifacts.appicons.logfunc') as log:
                selected = _app_icon_sources(context(root,[main,alias]))
            self.assertEqual(selected,[str(alias)])
            self.assertIn('unreadable database state',log.call_args.args[0])

    def test_symlink_mains_and_valid_or_dangling_sidecars_are_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            main, _ = make_database(root)
            alias = copy_to(main, root, 'data/user/0')
            linked = pathlib.Path(root) / 'data/user/10' / TAIL
            linked.parent.mkdir(parents=True)
            linked.symlink_to(main)
            dangling = pathlib.Path(root) / 'data/user/11' / TAIL
            dangling.parent.mkdir(parents=True)
            dangling.symlink_to(pathlib.Path(root) / 'missing-main')
            target = pathlib.Path(root) / 'other-state-wal'
            target.write_bytes(b'other physical state')
            wal = pathlib.Path(str(main) + '-wal')
            wal.symlink_to(target)
            journal = pathlib.Path(str(alias) + '-journal')
            journal.symlink_to(pathlib.Path(root) / 'missing-journal')
            with patch('scripts.artifacts.appicons.logfunc') as log:
                self.assertEqual(_app_icon_sources(context(root, [main, alias, linked, dangling])), [])
            self.assertEqual(sum('symlink main' in c.args[0] for c in log.call_args_list), 2)
            self.assertEqual(sum('unreadable database state' in c.args[0] for c in log.call_args_list), 2)
            # An actually absent sidecar remains acceptable after removing the link.
            journal.unlink()
            self.assertEqual(_app_icon_sources(context(root, [alias])), [str(alias)])
