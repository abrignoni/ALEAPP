"""Synthetic SQLite states exercise alias identity without asserting vendor schema."""
import hashlib
import pathlib
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from admin.test.scripts.test_withings_tracking_lookup import Context, make_room, make_lookup
from scripts.artifacts.WithingsHealthMate import healthmate_trackings, _tracking_state


class WithingsTrackingStatesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)

    def pair(self, view='data/data', name='stored'):
        parent = self.root / view / 'com.withings.wiscale2/databases'
        room, _ = make_room(parent / 'room-healthmate')
        lookup = make_lookup(parent / 'Withings-WiScale', [(37, name)])
        return room, lookup

    def parse(self, files):
        with patch('scripts.artifacts.WithingsHealthMate.logfunc') as log:
            output = healthmate_trackings.__wrapped__(Context(self.root, files))
        return (*output, log)

    def copy_pair(self, pair, view='data/user/0'):
        parent = self.root / view / 'com.withings.wiscale2/databases'
        parent.mkdir(parents=True, exist_ok=True)
        for source in pair:
            for suffix in ('', '-wal', '-shm', '-journal'):
                path = pathlib.Path(str(source) + suffix)
                if path.exists():
                    shutil.copy2(path, parent / path.name)
        return tuple(parent / path.name for path in pair)

    def test_equal_complete_alias_pairs_collapse_and_keep_repeats(self):
        pair = self.pair()
        alias = self.copy_pair(pair)
        headers, rows, source, _ = self.parse([*pair, *alias, pair[0]])
        self.assertEqual(len(headers), 12)
        self.assertEqual(len(rows), 14)
        self.assertEqual(rows[0], rows[-1])
        self.assertEqual(source.splitlines(), list(map(str, pair)))

    def test_different_lookup_wal_keeps_identical_room_states(self):
        pair = self.pair()
        writer = sqlite3.connect(pair[1])
        self.addCleanup(writer.close)
        writer.execute('PRAGMA journal_mode=WAL')
        writer.execute("UPDATE activityCategory SET name='first WAL'")
        writer.commit()
        alias = self.copy_pair(pair)
        writer.execute("UPDATE activityCategory SET name='second WAL'")
        writer.commit()
        self.assertEqual(pair[0].read_bytes(), alias[0].read_bytes())
        self.assertEqual(pair[1].read_bytes(), alias[1].read_bytes())
        hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                  [pair[0], pair[1], pathlib.Path(str(pair[1])+'-wal'),
                   alias[0], alias[1], pathlib.Path(str(alias[1])+'-wal')]}
        headers, rows, source, _ = self.parse([*pair, *alias])
        self.assertEqual(len(headers), 13)
        self.assertEqual(len(rows), 28)
        self.assertEqual(rows[0][9], 'second WAL')
        self.assertEqual(rows[14][9], 'first WAL')
        self.assertNotEqual(rows[0][-1], rows[14][-1])
        self.assertEqual(source.splitlines(), list(map(str, (*pair, *alias))))
        self.assertTrue(all(hashlib.sha256(p.read_bytes()).hexdigest() == h for p, h in hashes.items()))

    def test_room_wal_states_keep_committed_rows_and_order(self):
        pair = self.pair()
        writer = sqlite3.connect(pair[0])
        self.addCleanup(writer.close)
        writer.execute('PRAGMA journal_mode=WAL')
        writer.execute('INSERT INTO Track SELECT * FROM Track LIMIT 1')
        writer.commit()
        alias = self.copy_pair(pair)
        writer.execute('INSERT INTO Track SELECT * FROM Track LIMIT 1')
        writer.commit()
        self.assertEqual(pair[0].read_bytes(), alias[0].read_bytes())
        headers, rows, _, _ = self.parse([*pair, *alias])
        self.assertEqual(len(headers), 13)
        self.assertEqual(len(rows), 31)
        self.assertEqual([row[-1] for row in rows[:16]], [str(pair[0].relative_to(self.root))]*16)
        self.assertEqual([row[-1] for row in rows[16:]], [str(alias[0].relative_to(self.root))]*15)

    def test_missing_lookup_and_namespaces_never_borrow_or_collapse(self):
        pair = self.pair()
        alias = self.copy_pair(pair)
        alias[1].unlink()
        views = ['data/user/10', 'data/user_de/0', 'prefix/data/data', 'unknown']
        extra = [self.copy_pair(pair, view) for view in views]
        headers, rows, _, _ = self.parse([*pair, alias[0], *[p for group in extra for p in group]])
        self.assertEqual(len(headers), 13)
        self.assertEqual(len(rows), 84)
        self.assertEqual(rows[14][11], 'missing-lookup')
        self.assertEqual(len(set(row[-1] for row in rows)), 6)

    def test_failures_empty_and_malformed_do_not_hide_later_room(self):
        pair = self.pair()
        empty = self.copy_pair(pair, 'empty/data/data')
        db = sqlite3.connect(empty[0]); db.execute('DELETE FROM Track'); db.commit(); db.close()
        short = self.copy_pair(pair, 'short/data/data')
        db = sqlite3.connect(short[0]); db.execute('DROP TABLE Track'); db.execute('CREATE TABLE Track (x)'); db.commit(); db.close()
        corrupt = self.copy_pair(pair, 'corrupt/data/data'); corrupt[0].write_bytes(b'corrupt')
        db = sqlite3.connect(pair[0]); db.execute('UPDATE Track SET c3=NULL WHERE c0=1'); db.commit(); db.close()
        headers, rows, source, log = self.parse([*short, *corrupt, *empty, *pair])
        self.assertEqual(len(headers), 12)
        self.assertEqual(len(rows), 13)
        messages = ' '.join(str(call) for call in log.call_args_list)
        for message in ['unsupported-room-schema', 'unreadable-room', 'invalid-tracking-row']:
            self.assertIn(message, messages)
        self.assertNotIn(str(empty[0]), source)
        self.assertIn(str(empty[1]), source)
        self.assertTrue(all(row[3] != 1 for row in rows))

    def test_many_malformed_rows_have_bounded_diagnostics(self):
        pair = self.pair()
        db = sqlite3.connect(pair[0])
        db.execute('UPDATE Track SET c3=NULL')
        db.execute('INSERT INTO Track SELECT * FROM Track')
        db.commit()
        db.close()
        headers, rows, _, log = self.parse(pair)
        self.assertEqual(len(headers), 12)
        self.assertEqual(rows, [])
        self.assertEqual(log.call_count, 21)
        self.assertIn('28 invalid tracking rows omitted', str(log.call_args))

    def test_blob_category_name_and_id_and_connections_close(self):
        pair = self.pair()
        db = sqlite3.connect(pair[0])
        db.execute('UPDATE Track SET c12=? WHERE c0=0', (b'raw ID',))
        db.commit()
        db.close()
        db = sqlite3.connect(pair[1])
        db.execute('INSERT INTO activityCategory VALUES (?,?)', (b'raw ID', b'raw name'))
        db.commit()
        db.close()
        original = sqlite3.connect
        closed = []
        opened = []

        class TrackedConnection(sqlite3.Connection):
            def close(self):
                closed.append(self)
                super().close()

        def connect(*args, **kwargs):
            result = original(*args, **kwargs, factory=TrackedConnection)
            opened.append(result)
            return result

        with patch('scripts.artifacts.WithingsHealthMate.sqlite3.connect', side_effect=connect):
            _, rows, _, _ = self.parse(pair)
        self.assertEqual(rows[0][8], b'raw ID')
        self.assertEqual(rows[0][9], b'raw name')
        self.assertEqual(rows[0], rows[-1])
        self.assertEqual(opened, closed[::-1])

    def test_actual_sqlite_rollback_journal_changes_pair_identity(self):
        pair = self.pair()
        writer = sqlite3.connect(pair[1])
        self.addCleanup(writer.close)
        writer.execute("UPDATE activityCategory SET name='uncommitted'")
        journal = pathlib.Path(str(pair[1])+'-journal')
        self.assertGreater(journal.stat().st_size, 0)
        alias = self.copy_pair(pair)
        writer.rollback()
        self.assertEqual(pair[1].read_bytes(), alias[1].read_bytes())
        headers, rows, _, _ = self.parse([*pair, *alias])
        self.assertEqual((len(headers), len(rows)), (13, 28))
        self.assertEqual(rows[0][9], 'stored')
        self.assertEqual(rows[14][9], 'stored')
        # This copied inactive SQLite journal proves identity, not hot-journal recovery.

    def test_journal_state_presence_and_symlink_are_not_equal(self):
        pair = self.pair()
        alias = self.copy_pair(pair)
        before = _tracking_state(alias[1])
        journal = pathlib.Path(str(alias[1])+'-journal')
        journal.write_bytes(b'')
        self.assertNotEqual(before, _tracking_state(alias[1]))
        headers, rows, _, _ = self.parse([*pair, *alias])
        self.assertEqual((len(headers), len(rows)), (13, 28))
        journal.unlink(); journal.symlink_to(pair[1])
        with self.assertRaises(OSError):
            _tracking_state(alias[1])


if __name__ == '__main__':
    unittest.main()
