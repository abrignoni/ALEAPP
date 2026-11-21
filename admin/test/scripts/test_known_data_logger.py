"""Unit tests for the KDL (Known-data logger) module's hash chain, current-version rule and user keys."""
import copy
import hashlib
import unittest

from scripts.artifacts import knownDataLogger as kdl


def _row():
    # Same vector as ChainTest.canonicalMatchesPython in the app and
    # test_chain_vector_matches_kotlin in tools/test_make_documentation.py (known-data-logger v0.3.0).
    return {"account": None, "action": "sent_message", "app_package": "com.example.chat", "app_version": "1.2",
            "boot_count": 3, "content": "Hé \"q\" \\ line\nnext \U0001F600 bell\u0007 del\u007f",
            "conversation_id": None, "counterpart": "phone B", "detail": None, "device_label": "phoneA",
            "direction": "out", "edited_utc_ms": 1700000000500, "elapsed_ms": 123456, "entry_id": "e1",
            "expected_artifacts": ["aleapp:x", "y"], "gnss_time_ms": None, "kind": "action",
            "network_time_ms": 1700000000000, "prev_hash": "abc", "profile_id": 1, "refers_to": None,
            "revision_n": 0, "reviewed": True, "scenario_id": "sc", "seq": 7, "source": "manual",
            "time_quality": "exact", "tz_id": "America/New_York", "tz_offset_min": -300,
            "utc_ms": 1700000000123, "window_s": 5.894}


def _chained(rows):
    previous = ''
    for row in sorted(rows, key=lambda r: r['seq']):
        row['prev_hash'] = previous
        row['row_hash'] = hashlib.sha256(kdl._chain_canonical(row).encode('ascii')).hexdigest()  # pylint: disable=protected-access
        previous = row['row_hash']
    return rows


class ChainTest(unittest.TestCase):
    def test_vector_matches_the_app(self):
        digest = hashlib.sha256(kdl._chain_canonical(_row()).encode('ascii')).hexdigest()  # pylint: disable=protected-access
        self.assertEqual('23843a77b64530aba2b30d3ddaac1b19013cfcf924101dd6e799fef6ae99ac44', digest)

    def test_intact_and_broken(self):
        rows = []
        for seq in (1, 2, 3):
            row = _row()
            row.update(seq=seq, entry_id=f'e{seq}')
            rows.append(row)
        rows = _chained(rows)
        self.assertTrue(kdl._verify_chain(rows).startswith('intact, 3 rows'))  # pylint: disable=protected-access
        changed = copy.deepcopy(rows)
        changed[1]['content'] = 'changed'
        self.assertEqual('BROKEN at seq 2: row content does not match its hash',
                         kdl._verify_chain(changed))  # pylint: disable=protected-access
        removed = [rows[0], rows[2]]
        self.assertEqual('BROKEN at seq 3: link to the previous row does not match',
                         kdl._verify_chain(removed))  # pylint: disable=protected-access

    def test_rows_without_hashes(self):
        row = _row()
        row.pop('prev_hash')
        self.assertTrue(kdl._verify_chain([row]).startswith('not present'))  # pylint: disable=protected-access


class CurrentTest(unittest.TestCase):
    def test_highest_revision_wins_and_tombstone_removes(self):
        rows = [
            {'entry_id': 'a', 'revision_n': 0, 'seq': 1, 'kind': 'action', 'content': 'old',
             'boot_count': 1, 'elapsed_ms': 10},
            {'entry_id': 'a', 'revision_n': 1, 'seq': 3, 'kind': 'action', 'content': 'new',
             'boot_count': 1, 'elapsed_ms': 10},
            {'entry_id': 'b', 'revision_n': 0, 'seq': 2, 'kind': 'action', 'boot_count': 1, 'elapsed_ms': 5},
            {'entry_id': 'b', 'revision_n': 1, 'seq': 4, 'kind': 'tombstone', 'boot_count': 1, 'elapsed_ms': 5},
        ]
        current = kdl._current(rows)  # pylint: disable=protected-access
        self.assertEqual([('a', 'new', 2)], [(r['entry_id'], r['content'], n) for r, n in current])

    def test_order_is_boot_then_time_since_boot(self):
        rows = [
            {'entry_id': 'late_clock', 'revision_n': 0, 'seq': 2, 'kind': 'action', 'boot_count': 2,
             'elapsed_ms': 1, 'utc_ms': 1},
            {'entry_id': 'early', 'revision_n': 0, 'seq': 1, 'kind': 'action', 'boot_count': 1,
             'elapsed_ms': 999, 'utc_ms': 9},
        ]
        self.assertEqual(['early', 'late_clock'],
                         [r['entry_id'] for r, _ in kdl._current(rows)])  # pylint: disable=protected-access


class UserTest(unittest.TestCase):
    def test_user_from_each_layout(self):
        cases = {
            'data/data/com.abrignoni.knowndatalogger/databases/kl.db': '0',
            'data/user/10/com.abrignoni.knowndatalogger/databases/kl.db': '10',
            'userdata/user/150/com.abrignoni.knowndatalogger/databases/kl.db': '150',
            'data_mirror/data_ce/null/11/com.abrignoni.knowndatalogger/databases/kl.db': '11',
            'data/media/10/Documents/kdl_x/manifest.json': '10',
            'storage/emulated/0/Documents/kdl_x/manifest.json': '0',
            'sdcard/Documents/kdl_x/manifest.json': '',
        }
        for path, user in cases.items():
            self.assertEqual(user, kdl._user(path), path)  # pylint: disable=protected-access


if __name__ == '__main__':
    unittest.main()
