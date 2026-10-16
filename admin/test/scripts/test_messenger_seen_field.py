"""Stored seen flags must survive without asserting answered-call meaning."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from admin.test.scripts.test_messenger_evidence_scope import create_fixture, run


def create_seen_fixture(root):
    files = create_fixture(root)
    target = next(p for p in files if str(p.relative_to(root)) ==
                  'A/data/data/com.facebook.orca/databases/msys_database_42')
    db = sqlite3.connect(target)
    db.execute('DELETE FROM call_log')
    values = (None, 0, 1, 2, -1, 'unknown')
    for index, value in enumerate(values):
        db.execute('INSERT INTO call_log VALUES(?,?,?,?,?,?)',
                   (1700000000000+index*1000, 5+index, 1, 2, value, 42 if index%2 else 999))
    db.commit()
    db.close()
    return target, values


class TestMessengerSeenField(unittest.TestCase):
    def test_stored_values_and_unmatched_contacts(self):
        with tempfile.TemporaryDirectory() as directory:
            target, values = create_seen_fixture(Path(directory))
            headers, rows = run(directory, [target], 'get_fb_msys_calls')
            self.assertEqual(len(rows), len(values))
            self.assertNotIn('Call Answered', headers)
            self.assertEqual([row[headers.index('Has Been Seen (as stored)')] for row in rows],
                             list(values))
            self.assertEqual([row[headers.index('Party Name')] for row in rows],
                             [None, 'name', None, 'name', None, 'name'])
            self.assertEqual([row[0].timestamp() for row in rows],
                             [1700000000+index for index in range(6)])
            self.assertTrue(all(row[-1] == str(target.relative_to(directory)) for row in rows))


if __name__ == '__main__':
    unittest.main()
