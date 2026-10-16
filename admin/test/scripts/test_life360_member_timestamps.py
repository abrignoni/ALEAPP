"""Rows survive absent circles and unusable timestamps without changing stored values."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from scripts.artifacts import L360memberscircles as module


def create_fixture(root):
    path = Path(root)/'data/data/com.life360.android.safetymapd/databases/MembersEngineRoomDatabase'
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE members (id, circle_id, first_name, last_name, login_email, '
               'login_phone, avatar, is_admin, role, created_at, last_updated)')
    db.execute('CREATE TABLE circles (id, created_at, last_updated, name)')
    db.executemany('INSERT INTO circles VALUES (?,?,?,?)',
                   [('good', 1700000000, 1700000001000, 'circle'),
                    ('bad', 'nonnumeric', str(10**100), 'bad circle')])
    fixtures = [('valid', 'good', 1700000000, 1700000001000),
                ('unmatched', 'missing', None, 1700000001000),
                ('invalid', 'bad', 'bad', str(10**100)),
                ('later', 'good', 1700000002, 1700000003000),
                ('later', 'good', 1700000002, 1700000003000)]
    for member, circle, created, updated in fixtures:
        db.execute('INSERT INTO members VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                   (member, circle, '<name>', 'last', 'email', 'phone', 'avatar', 0,
                    'role', created, updated))
    db.commit()
    db.close()
    return path


class Context:
    def __init__(self, path):
        self.path = path

    def get_files_found(self):
        return [str(self.path)]


class TestLife360MemberTimestamps(unittest.TestCase):
    def test_rows_and_raw_values_survive_bad_timestamps(self):
        with tempfile.TemporaryDirectory() as root:
            path = create_fixture(root)
            headers, rows, source = module.Life360_MemberCircles.__wrapped__(Context(path))
            self.assertEqual(source, str(path))
        self.assertEqual(len(rows), 5)
        self.assertEqual([r[4] for r in rows], ['valid', 'unmatched', 'invalid', 'later', 'later'])
        self.assertEqual([h[1] for h in headers[:4]], ['datetime']*4)
        self.assertIsNone(rows[1][0])
        self.assertIsNotNone(rows[1][1])
        self.assertEqual(rows[1][2:4], (None, None))
        self.assertEqual(rows[2][:4], (None, None, None, None))
        self.assertEqual(rows[2][13:15], ('bad', str(10**100)))
        self.assertEqual(rows[2][15], 'nonnumeric')
        self.assertEqual(rows[3], rows[4])
        self.assertEqual(rows[0][5:13], ('<name>', 'last', 'email', 'phone', 'avatar', 0,
                                        'role', 'circle'))


if __name__ == '__main__':
    unittest.main()
