"""SQLite-generated WAL frames retain observations with local schema and provenance."""
from pathlib import Path
import shutil
import sqlite3
import struct
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlparse
from scripts.artifacts import L360noshowalerts as module

COLUMNS = ('id', 'type', 'last_updated', 'trigger_condition', 'critical_alert', 'run_at',
           'place_id', 'observed_user_id', 'creator_id', 'circle_id', 'daily')


def create_pair(root, user='0', reordered=False, count=1, overflow=False, schema_change=False, repeated=False, page_size=512, integer_pk=False):
    directory = Path(root)/f'data/user/{user}/com.life360.android.safetymapd/databases'
    directory.mkdir(parents=True, exist_ok=True)
    target = directory/'NoShowAlertRoomDatabase'
    with tempfile.TemporaryDirectory() as temp:
        working = Path(temp)/'source.db'
        db = sqlite3.connect(working)
        db.execute(f'PRAGMA page_size={page_size}')
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA wal_autocheckpoint=0')
        for number in range(4):
            db.execute(f'CREATE TABLE unrelated{number} (value)')
        db.commit()
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        columns = list(reversed(COLUMNS)) if reordered else list(COLUMNS)
        declarations = ['id INTEGER PRIMARY KEY' if integer_pk and c == 'id' else c
                        for c in columns]
        db.execute('CREATE TABLE no_show_alerts ('+','.join(declarations)+')')
        db.commit()
        for index in range(count):
            identifier = index + 1 if integer_pk else 'same' if count == 1 else f'id{index}'
            values = dict(zip(COLUMNS, (identifier, 'type',
                                        1700000000000, 'trigger', 0, 1700000000000000000,
                                        'place', 'observed', user, 'circle', 'daily')))
            if overflow:
                values['trigger_condition'] = 'x'*5000
            db.execute('INSERT INTO no_show_alerts VALUES ('+','.join('?' for _ in columns)+')',
                       [values[c] for c in columns])
        db.commit()
        if schema_change:
            db.execute("ALTER TABLE no_show_alerts ADD COLUMN additional")
            db.commit()
        if count == 1 and not overflow:
            db.execute('UPDATE no_show_alerts SET last_updated=1700000001000')
            db.commit()
            if repeated:
                db.execute("UPDATE no_show_alerts SET daily='different'")
                db.commit()
                db.execute("UPDATE no_show_alerts SET daily='daily'")
                db.commit()
        for suffix in ['', '-wal', '-shm']:
            shutil.copy2(Path(str(working)+suffix), Path(str(target)+suffix))
        db.close()
    return target


class Context:
    def __init__(self, root, files):
        self.root, self.files = Path(root), files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


class TestLife360WalSchema(unittest.TestCase):
    def test_relocated_reordered_multiple_pairs(self):
        with tempfile.TemporaryDirectory() as root:
            first = create_pair(root)
            second = create_pair(root, '10', reordered=True)
            files = [second, Path(str(first)+'-wal'), first, Path(str(second)+'-wal')]
            with patch.object(module, 'logfunc'):
                headers, rows, _ = module.Life360_NoShowAlerts.__wrapped__(Context(root, files))
            self.assertEqual(len(rows), 6)  # Two live rows plus four frame observations.
            self.assertEqual([h[1] for h in headers[:2]], ['datetime', 'datetime'])
            recovered = [r for r in rows if r[10] == 'Recovered from WAL']
            self.assertEqual(len(recovered), 4)
            self.assertEqual({r[3] for r in recovered}, {1700000000000, 1700000001000})
            self.assertTrue(all(r[13] != 4 for r in recovered))
            for row in recovered:
                self.assertEqual(row[5:9], ('trigger', 'type', 'place', 'observed'))
                self.assertEqual(row[15], row[14]+'-wal')
                self.assertIn(f'/user/{row[9]}/', row[14])

    def test_historical_schema_is_not_final_schema(self):
        with tempfile.TemporaryDirectory() as root:
            main = create_pair(root, schema_change=True)
            with patch.object(module, 'logfunc'):
                rows = module.recover_wal_observations(main, Path(str(main)+'-wal'))
            self.assertEqual([r['last_updated'] for r in rows],
                             [1700000000000, 1700000001000])
            self.assertNotIn('additional', rows[0])
            self.assertIn('additional', rows[1])

    def test_repeated_observations_and_broken_later_frame(self):
        with tempfile.TemporaryDirectory() as root:
            main = create_pair(root, repeated=True)
            wal = Path(str(main)+'-wal')
            with patch.object(module, 'logfunc'):
                rows = module.recover_wal_observations(main, wal)
            self.assertEqual(len(rows), 4)
            self.assertEqual(rows[1]['last_updated'], rows[3]['last_updated'])
            self.assertEqual(rows[1]['daily'], rows[3]['daily'])
            self.assertNotEqual(rows[1]['_wal_frame'], rows[3]['_wal_frame'])
            damaged = bytearray(wal.read_bytes())
            frame_size = 24 + int.from_bytes(damaged[8:12], 'big')
            damaged[len(damaged)-frame_size+16] ^= 1
            wal.write_bytes(damaged)
            with patch.object(module, 'logfunc') as log:
                remaining = module.recover_wal_observations(main, wal)
            self.assertEqual(len(remaining), 3)
            self.assertTrue(any('stopped validated prefix' in c.args[0]
                                for c in log.call_args_list))

    def test_invalid_prefix_and_truncation(self):
        with tempfile.TemporaryDirectory() as root:
            main = create_pair(root)
            wal = Path(str(main)+'-wal')
            original = wal.read_bytes()
            size = int.from_bytes(original[8:12], 'big')
            for offset in [24, 32+8, 32+16]:
                damaged = bytearray(original)
                damaged[offset] ^= 1
                wal.write_bytes(damaged)
                with patch.object(module, 'logfunc') as log:
                    rows = module.recover_wal_observations(main, wal)
                self.assertEqual(rows, [])
                self.assertTrue(any('checksum' in c.args[0] for c in log.call_args_list))
            wal.write_bytes(original[:-10])
            with patch.object(module, 'logfunc') as log:
                rows = module.recover_wal_observations(main, wal)
            self.assertLessEqual(len(rows), 2)
            self.assertTrue(any('truncated' in c.args[0] for c in log.call_args_list))
            self.assertEqual(size, 512)

    def test_interior_and_overflow_are_explicit_limits(self):
        with tempfile.TemporaryDirectory() as root:
            for user, count, overflow in [('0', 150, False), ('10', 1, True)]:
                main = create_pair(root, user, count=count, overflow=overflow)
                with patch.object(module, 'logfunc') as log:
                    rows = module.recover_wal_observations(main, Path(str(main)+'-wal'))
                self.assertEqual(rows, [])
                messages = ' '.join(c.args[0] for c in log.call_args_list)
                if count > 1:
                    self.assertTrue('interior' in messages or 'resolvable alert schema' in messages)
                else:
                    self.assertTrue('overflow' in messages or 'resolvable alert schema' in messages)

    def test_snapshot_fallback_without_deserialize_api(self):
        class LegacyConnection:
            def __init__(self, connection):
                self.connection = connection

            def execute(self, *args):
                return self.connection.execute(*args)

            def close(self):
                self.connection.close()

        connect = sqlite3.connect

        def legacy_connect(*args, **kwargs):
            return LegacyConnection(connect(*args, **kwargs))

        with tempfile.TemporaryDirectory() as root:
            main = create_pair(root, schema_change=True)
            wal = Path(str(main)+'-wal')
            before = (main.read_bytes(), wal.read_bytes())
            with patch.object(module.sqlite3, 'connect', side_effect=legacy_connect) as calls:
                with patch.object(module, 'logfunc'):
                    rows = module.recover_wal_observations(main, wal)
            self.assertEqual([r['last_updated'] for r in rows],
                             [1700000000000, 1700000001000])
            snapshots = [call.args[0] for call in calls.call_args_list
                         if str(call.args[0]).startswith('file:')]
            self.assertTrue(snapshots)
            self.assertTrue(all('mode=ro&immutable=1' in uri for uri in snapshots))
            self.assertEqual(before, (main.read_bytes(), wal.read_bytes()))
            self.assertTrue(all(not Path(unquote(urlparse(uri).path)).parent.exists()
                                for uri in snapshots))

    def test_large_sqlite_pages_preserve_wal_observations(self):
        with tempfile.TemporaryDirectory() as root:
            main = create_pair(root, page_size=65536)
            self.assertEqual(main.read_bytes()[16:18], b'\x00\x01')
            with patch.object(module, 'logfunc'):
                rows = module.recover_wal_observations(main, Path(str(main)+'-wal'))
            self.assertEqual([row['last_updated'] for row in rows],
                             [1700000000000, 1700000001000])
            invalid = bytearray(main.read_bytes())
            invalid[16:18] = b'\x00\x00'
            main.write_bytes(invalid)
            with patch.object(module, 'logfunc') as log:
                self.assertEqual(module.recover_wal_observations(
                    main, Path(str(main)+'-wal')), [])
            self.assertTrue(any('page size' in call.args[0] for call in log.call_args_list))

    def test_integer_primary_key_layout_is_explicitly_unsupported(self):
        with tempfile.TemporaryDirectory() as root:
            main = create_pair(root, integer_pk=True)
            with patch.object(module, 'logfunc') as log:
                rows = module.recover_wal_observations(main, Path(str(main)+'-wal'))
            self.assertEqual(rows, [])
            self.assertTrue(any('INTEGER PRIMARY KEY' in call.args[0]
                                for call in log.call_args_list))
            context = Context(root, [main, Path(str(main)+'-wal')])
            with patch.object(module, 'logfunc'):
                _, rows, _ = module.Life360_NoShowAlerts.__wrapped__(context)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][2], 1)  # SQLite live query resolves the rowid alias.

    def test_serial_bounds_and_schema_count(self):
        page = bytearray(512)
        page[0] = 13
        page[3:5] = struct.pack('>H', 1)
        page[8:10] = struct.pack('>H', 510)
        page[510:] = bytes([127, 1])
        rows, failures = module.parse_leaf_records(page, COLUMNS, 512)
        self.assertEqual(rows, [])
        self.assertTrue(failures)


if __name__ == '__main__':
    unittest.main()
