"""Raw contact flags preserve unknown values and missing source columns."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from admin.test.scripts.test_messenger_evidence_scope import run

VALUES = (None, '', 0, 1, 2, -1, 'unknown')


def create_flag_fixture(root):
    root = Path(root)
    files = []
    for user, missing in [(0, False), (10, True)]:
        path = root/f'A/data/user/{user}/com.facebook.orca/databases/threads_db2'
        path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(path)
        fields = ['user_key', 'first_name', 'last_name', 'username', 'profile_pic_square',
                  'is_friend', 'friendship_status', 'contact_relationship_status']
        if not missing:
            fields.append('is_messenger_user')
        db.execute('CREATE TABLE thread_users ('+','.join(fields)+')')
        for index, value in enumerate((None,) if missing else (*VALUES, VALUES[-1])):
            row = [f'FACEBOOK:{6 if index == 7 else index}', 'name', 'last', 'user', '[]',
                   1, 2, 3]
            if not missing:
                row.append(value)
            db.execute('INSERT INTO thread_users VALUES ('+','.join('?' for _ in row)+')', row)
        db.commit()
        db.close()
        files.append(path)
    return files


class TestMessengerRawUserFlag(unittest.TestCase):
    def test_null_unknown_missing_column_and_repeated_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_flag_fixture(directory)
            headers, rows = run(directory, files, 'get_fb_threads_contacts')
            self.assertEqual(len(rows), 9)
            self.assertNotIn('Is Messenger User', headers)
            index = headers.index('Is Messenger User (as stored)')
            self.assertEqual([row[index] for row in rows], [*VALUES, 'unknown', None])
            self.assertEqual([row[headers.index('Is Friend')] for row in rows], ['Yes']*9)
            self.assertEqual([row[headers.index('Friendship Status')] for row in rows], [2]*9)
            self.assertEqual([row[headers.index('Contact Relationship Status')] for row in rows],
                             [3]*9)
            self.assertEqual(rows[-1][-1], str(files[-1].relative_to(directory)))
            self.assertEqual(run(directory, list(reversed(files)), 'get_fb_threads_contacts')[1],
                             [rows[-1], *rows[:-1]])


if __name__ == '__main__':
    unittest.main()
